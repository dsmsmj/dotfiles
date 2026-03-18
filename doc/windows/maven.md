# Windows：安装与使用 Maven

Maven 是 Java 生态最常见的构建工具之一。Windows 上使用 Maven 的核心是：**先有 JDK**，并正确配置 `JAVA_HOME`（必要时再配置 `MAVEN_HOME` / PATH）。

## 安装 JDK（必须）

你可以任选一种方式（按公司环境选择）：

- **Microsoft Build of OpenJDK**：`https://learn.microsoft.com/java/openjdk/`
- **Eclipse Temurin (Adoptium)**：`https://adoptium.net/`

安装后验证：

```powershell
java -version
javac -version
where java
```

## 配置 JAVA_HOME（推荐）

1. 打开“系统属性 → 高级 → 环境变量”
2. 新建（或修改）系统变量：
   - `JAVA_HOME` = 你的 JDK 安装目录（示例：`C:\Program Files\Java\jdk-21`）
3. 在系统变量 `Path` 中添加：`%JAVA_HOME%\bin`

新开 PowerShell 验证：

```powershell
echo $env:JAVA_HOME
java -version
```

## 安装 Maven

### 方式 A：Scoop（推荐）

```powershell
scoop install maven
```

验证：

```powershell
mvn -v
where mvn
```

### 方式 B：Chocolatey

```powershell
choco install maven -y
```

### 方式 C：手动安装（可控但步骤多）

1. 下载 Maven Binary zip：`https://maven.apache.org/download.cgi`
2. 解压到例如：`C:\dev\apache-maven-3.9.9`
3. 配置环境变量：
   - `MAVEN_HOME` = `C:\dev\apache-maven-3.9.9`
   - 在 `Path` 添加：`%MAVEN_HOME%\bin`
4. 新开终端验证：

```powershell
mvn -v
```

## 常用命令

```powershell
mvn -v
mvn -q -DskipTests package
mvn test
mvn clean
mvn clean install
```

## Maven 仓库与镜像（可选）

Maven 的本地仓库默认在：

- `%USERPROFILE%\.m2\repository`

如果你需要配置镜像/私服，编辑：

- `%USERPROFILE%\.m2\settings.xml`

常见场景是公司 Nexus/Artifactory：把镜像、认证、proxy 写到 `settings.xml`。

## 常见问题（Windows）

### 1) `mvn` 运行报 “JAVA_HOME is not defined correctly”

优先检查：

- `echo $env:JAVA_HOME` 是否指向 **JDK 根目录**（不是 `bin` 目录）
- `where java` 是否命中你期望的 JDK
- 改完环境变量后是否 **新开终端**

### 2) 多个 JDK 共存导致版本错乱

如果你装过多个 JDK，`Path` 顺序很关键。一般做法是只在 `Path` 放 `%JAVA_HOME%\bin`，并通过改 `JAVA_HOME` 来切换。

