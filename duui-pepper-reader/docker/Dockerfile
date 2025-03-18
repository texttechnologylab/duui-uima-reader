# Use an official Maven image with JDK 23
FROM maven:3.9.9-eclipse-temurin-23

ADD src src
ADD pepper pepper
ADD pom.xml pom.xml
RUN mvn compile -X
CMD mvn exec:java -Dexec.mainClass="org.texttechnologylab.SaltyPepper.API"