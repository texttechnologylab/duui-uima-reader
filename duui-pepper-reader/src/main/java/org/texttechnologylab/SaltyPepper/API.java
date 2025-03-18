package org.texttechnologylab.SaltyPepper;

import de.tudarmstadt.ukp.dkpro.core.api.metadata.type.DocumentMetaData;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import com.sun.net.httpserver.HttpExchange;
import com.sun.net.httpserver.HttpHandler;
import com.sun.net.httpserver.HttpServer;
import org.apache.uima.UIMAException;
import org.apache.uima.cas.impl.XmiCasDeserializer;
import org.apache.uima.cas.impl.XmiCasSerializer;
import org.apache.uima.cas.impl.XmiSerializationSharedData;
import org.apache.uima.fit.factory.JCasFactory;
import org.apache.uima.fit.factory.TypeSystemDescriptionFactory;
import org.apache.uima.jcas.JCas;
import org.apache.uima.resource.ResourceInitializationException;
import org.apache.uima.resource.metadata.TypeSystemDescription;
import org.json.JSONArray;
import org.json.JSONException;
import org.json.JSONObject;
import org.texttechnologylab.annotation.AnnotationComment;
import org.texttechnologylab.annotation.type.Taxon;
import org.texttechnologylab.utilities.helper.FileUtils;
import org.texttechnologylab.utilities.helper.TempFileHandler;
import org.xml.sax.SAXException;

import java.io.*;
import java.net.InetSocketAddress;
import java.nio.charset.Charset;

import com.sun.net.httpserver.HttpHandler;
import com.sun.net.httpserver.HttpServer;
import org.apache.uima.fit.factory.TypeSystemDescriptionFactory;

import java.net.InetSocketAddress;
import java.nio.charset.StandardCharsets;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.Paths;
import java.util.*;
import java.util.concurrent.ConcurrentLinkedQueue;
import java.util.concurrent.CopyOnWriteArrayList;
import java.util.concurrent.atomic.AtomicInteger;
import java.util.zip.ZipEntry;
import java.util.zip.ZipInputStream;

public class API {
    private static final Logger LOGGER = LoggerFactory.getLogger(API.class);
    private static Queue<Path> fileQueue = new ConcurrentLinkedQueue<>();
    private static Converter converter = new Converter();
    private static final AtomicInteger clock = new AtomicInteger(0);

    public static void main(String[] args) throws Exception {
        try {
            HttpServer server = HttpServer.create(new InetSocketAddress(9714), 0);
            server.createContext("/v1/communication_layer", new CommunicationLayer());
            server.createContext("/v1/typesystem", new TypesystemHandler());
            server.createContext("/v1/test", new MyHandler());
            server.createContext("/v1/process", new ProcessHandler());
            server.createContext("/v1/init", new InitHandler());
            server.createContext("/v1/details/input_output", new IOHandler());
            server.setExecutor(null);
            server.start();
            LOGGER.info("Server started on port 9714");
        } catch (Exception e) {
            LOGGER.error("Server failed to start", e);
        }
    }

    static class MyHandler implements HttpHandler {
        @Override
        public void handle(HttpExchange t) throws IOException {
            LOGGER.info("{} {}", t.getRequestMethod(), t.getRequestURI());
            String response = "This is the response";
            t.sendResponseHeaders(200, response.length());
            OutputStream os = t.getResponseBody();
            os.write(response.getBytes());
            os.close();
        }
    }


    static class ProcessHandler implements HttpHandler {
        static JCas jc;

        static {
            try {
                jc = JCasFactory.createJCas();
            } catch (UIMAException e) {
                e.printStackTrace();
            }
        }

        @Override
        public void handle(HttpExchange t) throws IOException {
            LOGGER.info("{} {}", t.getRequestMethod(), t.getRequestURI());
            try {
                jc.reset();

                // XmiSerializationSharedData sharedData = new XmiSerializationSharedData();

                // XmiCasDeserializer.deserialize(t.getRequestBody(), jc.getCas(), true ,sharedData);

                Path currentPath = fileQueue.poll();

                if (currentPath != null) {
                    String fileName = currentPath.getFileName().toString();

                    // Extract "01" by removing the extension
                    String baseName = fileName.substring(0, fileName.lastIndexOf(".txt"));

                    String content = Files.readString(currentPath);
                    jc.setDocumentText(content);

                    DocumentMetaData dmd = new DocumentMetaData(jc);
                    dmd.setDocumentId(String.valueOf(clock.decrementAndGet()));
                    dmd.setDocumentTitle(baseName);
                    dmd.addToIndexes();

                }

                t.sendResponseHeaders(200, 0);
                //XmiCasSerializer.serialize(jc.getCas(), null, t.getResponseBody(), false, sharedData);
                XmiCasSerializer.serialize(jc.getCas(), null, t.getResponseBody());

                t.getResponseBody().close();
            } catch (Exception e) {
                e.printStackTrace();
                t.sendResponseHeaders(404, -1);
            }

            t.getResponseBody().close();
        }
    }

    static class TypesystemHandler implements HttpHandler {
        @Override
        public void handle(HttpExchange t) throws IOException {
            LOGGER.info("{} {}", t.getRequestMethod(), t.getRequestURI());
            try {
                TypeSystemDescription desc = TypeSystemDescriptionFactory.createTypeSystemDescription();
                StringWriter writer = new StringWriter();
                desc.toXML(writer);
                String response = writer.getBuffer().toString();

                t.sendResponseHeaders(200, response.getBytes(Charset.defaultCharset()).length);

                OutputStream os = t.getResponseBody();
                os.write(response.getBytes(Charset.defaultCharset()));

            } catch (ResourceInitializationException e) {
                e.printStackTrace();
                t.sendResponseHeaders(404, -1);
                return;
            } catch (SAXException e) {
                e.printStackTrace();
            } finally {
                t.getResponseBody().close();
            }

        }
    }

    static class IOHandler implements HttpHandler {
        @Override
        public void handle(HttpExchange t) throws IOException {
            LOGGER.info("{} {}", t.getRequestMethod(), t.getRequestURI());
            try {
                JSONObject rObject = new JSONObject();
                rObject.put("input", new JSONArray());
                rObject.put("output", new JSONArray());
                String response = rObject.toString();
                t.sendResponseHeaders(200, response.getBytes(Charset.defaultCharset()).length);

                OutputStream os = t.getResponseBody();
                os.write(response.getBytes(Charset.defaultCharset()));

            } catch (JSONException e) {
                e.printStackTrace();
                t.sendResponseHeaders(404, -1);
                return;
            } finally {
                t.getResponseBody().close();
            }

        }
    }

    static class InitHandler implements HttpHandler {
        @Override
        public void handle(HttpExchange t) throws IOException {
            if (!"POST".equalsIgnoreCase(t.getRequestMethod())) {
                sendResponse(t, 405, "Method Not Allowed");
                return;
            }

            String contentType = t.getRequestHeaders().getFirst("Content-Type");
            if (contentType == null || !contentType.contains("multipart/form-data")) {
                sendResponse(t, 400, "Bad Request: Expected multipart/form-data");
                return;
            }

            // Extract boundary from Content-Type header
            String boundary = contentType.split("boundary=")[1].trim();
            InputStream inputStream = t.getRequestBody();

            byte[] zipBytes = extractZipFromMultipart(inputStream, boundary);
            if (zipBytes == null) {
                sendResponse(t, 400, "Bad Request: No valid zip file found");
                return;
            }

            if (clock.get() <= 0) {
                // Save the ZIP file to a temporary location
                File tempFile = Files.createTempFile("received_", ".zip").toFile();
                try (FileOutputStream fos = new FileOutputStream(tempFile)) {
                    fos.write(zipBytes);
                }

                // Create temp dirs
                Path tempUnzip = Files.createTempDirectory("tempUnzip");
                Path tempTextDir = Files.createTempDirectory("tempTextDir");
                // UNZIP
                unzipRecursive(tempFile.toPath(), tempUnzip);
                // clean up temp zip file
                deleteFile(tempFile.toPath());
                // convert all to .txt directory
                converter.convertAnyToAny(tempUnzip.toAbsolutePath().toString(), tempTextDir.toAbsolutePath().toString());
                // clean up unzip directory
                deleteDirectory(tempUnzip.toAbsolutePath());
                // find all .txt files in temp
                List<Path> txtFiles = findTxtFiles(tempTextDir.toAbsolutePath());
                fileQueue.addAll(txtFiles);
                System.out.println(tempTextDir.toAbsolutePath());
                clock.getAndAdd(txtFiles.size());
                // Send response (modify "0" to reflect actual nDocs if needed)
                sendResponse(t, 200, String.format("{\"n_docs\": %d}", txtFiles.size()));
            } else {
                sendResponse(t, 200, "{\"n_docs\": 0}");
            }
        }

        private void sendResponse(HttpExchange t, int statusCode, String response) throws IOException {
            byte[] responseBytes = response.getBytes(StandardCharsets.UTF_8);
            t.getResponseHeaders().set("Content-Type", "application/json");
            t.sendResponseHeaders(statusCode, responseBytes.length);
            try (OutputStream os = t.getResponseBody()) {
                os.write(responseBytes);
            }
        }

        // Function to delete a single file
        private static void deleteFile(Path file) throws IOException {
            if (Files.exists(file)) {
                Files.delete(file);
            }
        }

        // Function to delete a directory and its contents recursively
        private static void deleteDirectory(Path directory) throws IOException {
            if (Files.exists(directory)) {
                Files.walk(directory)
                        .sorted((a, b) -> b.compareTo(a)) // Delete files before directories
                        .forEach(path -> {
                            try {
                                Files.delete(path);
                            } catch (IOException e) {
                                System.err.println("Failed to delete " + path + ": " + e.getMessage());
                            }
                        });
            }
        }

        // Function to find all .txt files in a directory and its subdirectories
        private static List<Path> findTxtFiles(Path directory) throws IOException {
            List<Path> txtFiles = new ArrayList<>();

            // Check if the directory exists and is actually a directory
            if (!Files.exists(directory)) {
                throw new IllegalArgumentException("Directory does not exist: " + directory);
            }
            if (!Files.isDirectory(directory)) {
                throw new IllegalArgumentException("Path is not a directory: " + directory);
            }

            // Walk through the directory tree and filter for .txt files
            Files.walk(directory)
                    .filter(Files::isRegularFile)           // Only regular files (not directories)
                    .filter(path -> path.toString().endsWith(".txt")) // Ends with .txt
                    .forEach(txtFiles::add);               // Add to the list

            return txtFiles;
        }

        private byte[] extractZipFromMultipart(InputStream inputStream, String boundary) throws IOException {
            ByteArrayOutputStream buffer = new ByteArrayOutputStream();
            int b;
            while ((b = inputStream.read()) != -1) {
                buffer.write(b);
            }
            byte[] fullData = buffer.toByteArray();

            String boundaryStart = "--" + boundary;
            String boundaryEnd = "--" + boundary + "--";
            byte[] boundaryStartBytes = boundaryStart.getBytes(StandardCharsets.UTF_8);
            byte[] boundaryEndBytes = boundaryEnd.getBytes(StandardCharsets.UTF_8);

            // Find the start of the file content
            int contentStart = -1;
            int headersEnd = indexOf(fullData, "\r\n\r\n".getBytes(StandardCharsets.UTF_8), 0);
            if (headersEnd != -1) {
                contentStart = headersEnd + 4; // Skip past "\r\n\r\n"
            }

            // Find the end of the file content
            int contentEnd = indexOf(fullData, boundaryEndBytes, contentStart);
            if (contentEnd == -1) {
                contentEnd = indexOf(fullData, boundaryStartBytes, contentStart);
            }
            if (contentEnd == -1) {
                contentEnd = fullData.length; // Fallback to end of data
            }

            if (contentStart == -1 || contentEnd <= contentStart) {
                return null; // Invalid content range
            }

            // Extract the ZIP data
            byte[] zipData = Arrays.copyOfRange(fullData, contentStart, contentEnd);
            if (isZipFile(zipData)) {
                return zipData;
            }
            return null;
        }

        private int indexOf(byte[] data, byte[] pattern, int start) {
            for (int i = start; i <= data.length - pattern.length; i++) {
                boolean match = true;
                for (int j = 0; j < pattern.length; j++) {
                    if (data[i + j] != pattern[j]) {
                        match = false;
                        break;
                    }
                }
                if (match) return i;
            }
            return -1;
        }

        private boolean isZipFile(byte[] data) {
            return data.length >= 4 && data[0] == 0x50 && data[1] == 0x4B && data[2] == 0x03 && data[3] == 0x04;
        }
    }

    static class CommunicationLayer implements HttpHandler {
        @Override
        public void handle(HttpExchange t) throws IOException {
            LOGGER.info("{} {}", t.getRequestMethod(), t.getRequestURI());
            String response = "serial = luajava.bindClass(\"org.apache.uima.cas.impl.XmiCasSerializer\")\n" +
                    "deserial = luajava.bindClass(\"org.apache.uima.cas.impl.XmiCasDeserializer\")\n" +
                    "function serialize(inputCas,outputStream,params)\n" +
                    "  serial:serialize(inputCas:getCas(),outputStream)\n" +
                    "end\n" +
                    "\n" +
                    "function deserialize(inputCas,inputStream)\n" +
                    "  inputCas:reset()\n" +
                    "  deserial:deserialize(inputStream,inputCas:getCas(),true)\n" +
                    "end";
            t.sendResponseHeaders(200, response.length());
            OutputStream os = t.getResponseBody();
            os.write(response.getBytes());
            os.close();
        }
    }
    static void unzipRecursive(Path zipFile, Path destDir) throws IOException {
        try (ZipInputStream zis = new ZipInputStream(new FileInputStream(zipFile.toFile()))) {
            ZipEntry entry;
            while ((entry = zis.getNextEntry()) != null) {
                Path entryPath = destDir.resolve(entry.getName());

                if (entry.isDirectory()) {
                    Files.createDirectories(entryPath);
                } else {
                    // Ensure parent directories exist
                    Files.createDirectories(entryPath.getParent());

                    // Extract the file
                    try (FileOutputStream fos = new FileOutputStream(entryPath.toFile())) {
                        byte[] buffer = new byte[4096];
                        int bytesRead;
                        while ((bytesRead = zis.read(buffer)) != -1) {
                            fos.write(buffer, 0, bytesRead);
                        }
                    }
                    System.out.println("Extracted: " + entryPath.toAbsolutePath());

                    // If the extracted file is a zip, recurse
                    if (entry.getName().toLowerCase().endsWith(".zip")) {
                        // Recursively unzip nested zip
                        Path nestedDestDir = destDir.resolve(entry.getName().replace(".zip", ""));
                        unzipRecursive(entryPath, nestedDestDir);
                        // Delete the nested zip file after extraction
                        Files.deleteIfExists(entryPath);
                        System.out.println("Deleted nested zip: " + entryPath);
                    }
                }
                zis.closeEntry();
            }
        }
    }
}