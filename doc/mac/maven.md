# macOS：安装与使用 Maven

Maven 是 Java 生态最常见的构建工具之一。macOS 上推荐用 Homebrew 安装，并确保 JDK 已就绪。

## 安装 JDK（必须）

推荐用 Homebrew 安装 Temurin：

```bash
brew install --cask temurin
```

验证：

```bash
java -version
javac -version
which java
```

> 如果你需要特定版本（例如 17/21），可以改装对应 cask（如 `temurin17` / `temurin21`，以 Homebrew 实际提供为准）。

## 安装 Maven（推荐：Homebrew）

```bash
brew install maven
```

验证：

```bash
mvn -v
which mvn
```

## 常用命令

```bash
mvn -v
mvn -q -DskipTests package
mvn test
mvn clean
mvn clean install
```

## Maven 仓库与 settings.xml

Maven 的本地仓库默认在：

- `~/.m2/repository`

镜像/私服/认证配置在：

- `~/.m2/settings.xml`

公司常见是 Nexus/Artifactory：把 mirror、server credentials、proxy 写到 `settings.xml`。

## 常见问题（macOS）

### 1) `mvn` 报 JAVA_HOME 问题

先确认 JDK 真的可用：

```bash
java -version
```

必要时可用 macOS 自带的工具打印当前 JDK 路径：

```bash
/usr/libexec/java_home
```

