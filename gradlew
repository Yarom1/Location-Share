#!/bin/sh
GRADLE_WRAPPER_JAR="gradle/wrapper/gradle-wrapper.jar"
GRADLE_WRAPPER_PROPERTIES="gradle/wrapper/gradle-wrapper.properties"

# Download gradle wrapper jar if missing
if [ ! -f "$GRADLE_WRAPPER_JAR" ]; then
  mkdir -p gradle/wrapper
  curl -sL "https://github.com/gradle/gradle/raw/v8.3.0/gradle/wrapper/gradle-wrapper.jar" -o "$GRADLE_WRAPPER_JAR" 2>/dev/null || true
fi

exec java -jar "$GRADLE_WRAPPER_JAR" "$@"
