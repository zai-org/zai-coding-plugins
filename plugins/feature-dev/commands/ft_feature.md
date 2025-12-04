---
allowed-tools: all
argument-hint: [功能描述]
description: 生成原子级功能列表到 main_feature_list.md
---

# 功能生成

你是一个功能拆分专家。请将用户的需求拆分为原子级功能列表，并生成 `main_feature_list.md` 文件。

## 用户需求

$ARGUMENTS

## 功能要求

1. **分析用户需求**：仔细理解用户的功能描述

2. **需求完整性验证（关键！必须执行！）**：

   **需求梳理**：
   - 列出用户明确提出的所有需求
   - 识别隐性的必需需求（用户可能未明确说明但必需的功能）
   - 区分核心需求和可选需求
   - 识别紧急需求和一般需求

   **需求分类**：
   - **功能性需求**：系统应该做什么（用户可感知的功能）
   - **非功能性需求**：系统的质量属性（性能、安全、可靠性等）
   - **约束需求**：技术约束、业务约束、合规性要求
   - **接口需求**：与其他系统的交互、API集成等
   - **文档需求**：用户手册、API文档、部署文档等

   **需求完整性检查**（使用检查清单）：
   ```
   □ 功能需求是否全覆盖？
   □ 非功能性需求是否考虑？（性能、安全、可靠性）
   □ 异常处理是否覆盖？（错误处理、边界条件）
   □ 集成需求是否考虑？（系统集成、第三方集成）
   □ 文档需求是否覆盖？（用户文档、API文档）
   □ 部署需求是否考虑？（部署脚本、配置）
   □ 监控和日志是否包含？
   □ 测试需求是否覆盖？（单元测试、集成测试）
   ```

   **需求追溯矩阵**：
   - 建立需求到功能的追溯关系
   - 格式："[原始需求] → [原子级功能1, 原子级功能2, ...]"
   - 示例："用户注册功能 → 创建注册页面UI + 实现验证逻辑 + 实现API接口 + 实现邮件发送"

3. **拆分为原子级功能（强制！必须细致！）**：

   ⚠️ **重要警告**：如果不达到原子级，Sub-Agent会产生幻觉，声称完成实际没做的工作！

   **原子级功能定义**：一个原子级功能满足以下所有条件：
   - ✅ **单一职责**：只做一件具体的事情，只解决一个问题
   - ✅ **无法拆分**：不能拆分成更小的功能，拆分后就会破坏单一职责
   - ✅ **独立可执行**：不依赖其他功能的中间结果（可以依赖前置完成的文件）
   - ✅ **结果明确**：完成后有明确、可见的结果（文件、代码、配置等）
   - ✅ **时间可控**：单个功能能在合理时间内完成（通常30分钟-2小时，复杂度≤中等）
   - ✅ **可测试**：可以立即测试和验证，不需要其他功能配合
   - ✅ **可验证**：可以通过简单的检查（文件存在、代码运行、测试通过）来验证完成

   **拆分决策树（必须遵循！）**：
   ```
   是否是原子级功能？
   │
   ├─ 是 → ✅ 可以直接使用
   │
   └─ 否 → 这个功能可以分解为多个步骤？
           │
           ├─ 是 → ❌ 继续拆分
           │      │
           │      └─ 重复此决策过程，直到答案为"是"
           │
           ├─ 否 → 涉及多个文件或组件？
           │      │
           │      ├─ 是 → ❌ 继续拆分（每个文件/组件一个功能）
           │      │
           │      └─ 否 → 预估完成时间超过1小时？
           │           │
           │           ├─ 是 → ❌ 继续拆分
           │           │
           │           └─ 否 → 有多个不同的职责？
           │                │
           │                ├─ 是 → ❌ 继续拆分（每个职责一个功能）
           │                │
   │                └─ 否 → ✅ 这是原子级！
   ```

   **严格判断标准（必须全部通过！）**：

   ❌ **必须拆分的信号**（出现任何一个就必须继续拆分）：
   - 这个功能需要3个或更多步骤来完成
   - 这个功能涉及2个或更多文件或组件
   - 这个功能可以分解为"先做A，再做B"
   - 这个功能需要调用多个API或进行多个数据库操作
   - 预估完成时间超过1-2小时
   - 这个功能包含2个或更多不同的职责
   - 这个功能包含"和"或"、"或"、"以及"等连接词描述多个任务
   - ⚠️ **关键**：功能描述包含"分析"、"识别"、"设计"、"规划"、"抽离"、"迁移"、"重构"、"优化"、"改进"等抽象动词
   - ⚠️ **关键**：功能涉及分析代码、识别组件、抽离逻辑、迁移模块等抽象任务
   - ⚠️ **关键**：功能需要理解、分析、研究、调研等认知类动作
   - ⚠️ **关键**：功能涉及"查看"、"读取"、"理解"等探索性动作
   - ⚠️ **关键**：功能描述以模块、组件、系统、功能域等高层级为对象

   ✅ **可以不拆分的信号**（必须全部满足）：
   - 这个功能只是一个单一的文件创建（如"创建UserServiceImpl.java文件"）
   - 这个功能只是一个类或方法的实现（如"实现UserServiceImpl.registerUser方法"）
   - 这个功能只是一个配置项的添加（如"在pom.xml中添加spring-boot-starter-data-jdbc依赖"）
   - 这个功能只是一行代码的修改（如"在UserController第45行添加@RequestParam注解"）
   - 这个功能只是一个测试用例的编写（如"编写UserServiceImpl.registerUser的单元测试"）
   - 这个功能可以立即测试和验证（不需要其他功能配合）
   - 预估完成时间在30分钟-2小时以内
   - 这个功能只有一个明确的职责
   - 完成后可以立即看到结果（文件存在、代码运行、测试通过）
   - ⚠️ **关键**：功能对象是具体的文件、类、方法、配置项、代码行
   - ⚠️ **关键**：功能动词是"创建"、"添加"、"实现"、"修改"、"编写"、"配置"、"删除"等具体动作
   - ⚠️ **关键**：功能有明确的输入（具体文件路径）和输出（具体文件或代码）

   **依赖关系处理**：
   - 原子级功能可以是有依赖的，但要明确说明依赖关系
   - 依赖关系应该被文档化，在功能描述中标注
   - 有依赖的功能必须按依赖顺序执行，无依赖的功能可以并行
   - 示例："创建用户API（依赖：数据库表已创建）"

   **⚠️ 严禁的抽象功能类型（绝对禁止！）**：

   以下类型的功能必须继续拆分，直到到达具体的文件、类、方法级别：

   1. **分析类功能**（❌ 必须拆分）：
   ```
   ❌ "分析uc-framework中的基础设施代码"
   ❌ "识别数据库、缓存、消息队列等基础设施组件"
   ❌ "研究现有架构的设计模式"
   ❌ "理解当前系统的业务逻辑"

   ✅ 正确拆分到：
   [ ] 读取uc-framework/pom.xml文件内容
   [ ] 读取src/main/java/com/example/infrastructure/下的所有Java文件
   [ ] 创建analysis_report.md文件记录分析结果
   ```

   2. **识别类功能**（❌ 必须拆分）：
   ```
   ❌ "识别所有使用数据库的服务类"
   ❌ "识别需要重构的代码模块"
   ❌ "识别可复用的组件"

   ✅ 正确拆分到：
   [ ] 在pom.xml中搜索所有spring-boot-starter-data依赖
   [ ] 创建list_database_services.txt文件
   [ ] 将所有数据库服务类名写入文件
   ```

   3. **设计类功能**（❌ 必须拆分）：
   ```
   ❌ "设计新的基础设施架构"
   ❌ "设计用户认证流程"
   ❌ "设计数据库表结构"

   ✅ 正确拆分到：
   [ ] 创建DatabaseConfig.java文件
   [ ] 在DatabaseConfig中添加dataSourceBean方法
   [ ] 在DatabaseConfig中添加jdbcTemplateBean方法
   [ ] 创建UserTable.sql文件
   [ ] 在UserTable.sql中添加CREATE TABLE语句
   ```

   4. **抽离/迁移类功能**（❌ 必须拆分）：
   ```
   ❌ "从uc-framework中抽离基础设施代码"
   ❌ "迁移配置文件到新模块"
   ❌ "重构代码到新模块"

   ✅ 正确拆分到：
   [ ] 创建uc-infrastructure/pom.xml文件
   [ ] 复制uc-framework/src/main/java/com/example/db/到uc-infrastructure/src/main/java/com/example/infrastructure/db/
   [ ] 在uc-infrastructure/pom.xml中添加spring-boot-starter-data-jdbc依赖
   [ ] 修改复制文件中的包名从com.example.db到com.example.infrastructure.db
   [ ] 在uc-framework/pom.xml中移除spring-boot-starter-data-jdbc依赖
   [ ] 删除uc-framework/src/main/java/com/example/db/目录
   ```

   5. **配置类功能**（⚠️ 可以原子级，但要具体）：
   ```
   ❌ "配置数据库连接" → 太大
   ⚠️ "配置数据库连接参数" → 还是太大
   ✅ "在application.properties中添加spring.datasource.url=jdbc:mysql://localhost:3306/mydb"
   ✅ "在pom.xml中添加spring-boot-starter-data-jdbc依赖"
   ✅ "创建DatabaseConfig.java类并添加@Configuration注解"
   ```

   **⚠️ 关键规则：执行步骤必须独立成功能（实战经验！）**：

   从奥特曼卡牌PK案例中发现的问题：

   ❌ **错误示例**：
   ```
   [ ] 创建Android项目基础结构和配置
     执行步骤：
     1. 创建Android项目基础目录结构（多个目录）
     2. 配置build.gradle添加必要依赖（多个依赖）
     3. 配置AndroidManifest.xml（多个配置）
     4. 创建应用图标和基础资源文件（多个文件）
   ```

   ❌ **问题**：虽然功能标题是"创建xxx"，但执行步骤中包含多个不同的文件和配置，导致功能太大

   ✅ **正确做法**：
   ```
   [ ] 创建Android项目基础目录结构
   [ ] 配置build.gradle添加CameraX依赖
   [ ] 配置build.gradle添加OCR依赖
   [ ] 配置AndroidManifest.xml添加相机权限
   [ ] 配置AndroidManifest.xml添加存储权限
   [ ] 创建应用图标资源文件
   ```

   **执行步骤拆分规则（必须遵守！）**：

   1. **禁止将多个步骤打包为一个功能**
      - ❌ 禁止："执行步骤：1. xxx 2. xxx 3. xxx"
      - ✅ 必须：每个步骤独立成为一个功能
      - ✅ 格式：功能标题就是"创建xxx文件"或"添加xxx配置"

   2. **执行步骤应该作为拆分参考，而不是描述**
      - 执行步骤是告诉你如何拆分，而不是保留在功能描述中
      - 拆分后，执行步骤应该消失，只留下原子级功能

   3. **每个功能都应该只有一个执行步骤**
      - ✅ 好的：`[ ] 创建build.gradle文件` → 执行步骤：创建文件
      - ❌ 坏的：`[ ] 创建Android项目结构` → 执行步骤：1. 创建目录 2. 创建文件 3. 添加配置

   4. **功能描述中的"执行步骤"字段应该是空的或只有一行**
      - ✅ `执行步骤：创建build.gradle文件`
      - ❌ `执行步骤：1. 创建文件 2. 添加依赖 3. 配置`

   **检查清单（生成功能前必须检查！）**：
   ```
   ☐ 这个功能的"执行步骤"是否只有一行？
   ☐ 这个功能的"执行步骤"是否对应一个文件或一个配置项？
   ☐ 如果执行步骤有多行，是否应该拆分为多个功能？
   ☐ 是否可以将"执行步骤1"、"执行步骤2"等改为独立的功能标题？
   ```

   **原子级功能的最低标准（必须满足至少一个！）**：

   ⭐ **标准1：文件级别**（最常用和最合适）
   - 创建一个新文件（如"创建UserServiceImpl.java"）
   - 复制一个文件到新位置
   - 删除一个文件
   - 重命名一个文件
   - 移动一个文件到新目录
   - ✅ **文件是原子级的**：一个文件包含一组相关功能，无法再拆分为更小的独立单元

   ⭐ **标准2：方法级别**（独立的功能点）
   - 实现一个方法（如"实现UserServiceImpl.registerUser方法"）
   - 添加一个方法（如"在UserServiceImpl中添加public void updateUser方法"）
   - 修改一个方法（如"修改UserServiceImpl.registerUser的验证逻辑"）
   - ✅ **方法是原子级的**：一个方法完成单一职责的功能，无法再拆分

   ⚠️ **标准3：功能模块级别（不推荐，通常会继续拆分）**
   - ❌ 通常太大，不建议直接使用
   - ❌ 例如："用户认证模块" → 太大，包含登录、注册、Token验证等多个文件
   - ❌ 例如："用户注册功能模块" → 太大，包含Controller、Service、Validator等多个文件
   - ❌ 例如："订单处理模块" → 太大，包含创建、支付、发货等多个文件
   - ⚠️ **只有在极端情况下才使用**：多个文件共同完成一个极小且不可拆分的原子功能
   - ✅ **正确做法**：应该继续拆分到文件级别或方法级别
     "用户认证模块" → 拆分为：
       [ ] 创建AuthController.java文件
       [ ] 创建AuthService.java文件
       [ ] 创建JwtUtil.java文件
       [ ] 实现AuthService.loginUser方法
       [ ] 实现AuthService.registerUser方法
       [ ] 实现JwtUtil.generateToken方法
       [ ] 实现JwtUtil.verifyToken方法

   ⭐ **标准4：配置项级别**（单个配置修改）
   - 添加一个配置项（如"在pom.xml中添加spring-boot-starter-data-jdbc依赖"）
   - 修改一个配置值（如"修改application.properties中的端口号为8081"）
   - 添加一个注解（如"在类上添加@Service注解"）

   ⭐ **标准5：测试级别**
   - 编写一个测试类（如"编写UserServiceImplTest类"）
   - 编写一个测试方法（如"编写UserServiceImplTest.shouldRegisterUser测试方法"）

   ⚠️ **重要原则**：
   - 📌 **文件是基本原子级**：大多数情况下，创建/修改一个文件就是原子级
   - 📌 **方法是功能原子级**：一个方法完成单一职责，可以独立验证
   - 📌 **功能模块是独立原子级**：完整的业务功能，包含多个文件但整体不可拆分
   - 📌 **不可再拆分是核心**：无论哪个级别，判断标准是"是否可以继续拆分"
   - 📌 **可验证是关键**：完成后可以立即验证（文件存在、方法运行、功能正常）

   **必须细致化的场景（具体指导！）**：

   1. **API开发**：每个API端点都是一个原子级功能
      - ❌ "实现用户API" → 太大，包含多个端点
      - ❌ "实现用户注册功能" → 太大，包含UI、验证、API、邮件等多个步骤
      - ✅ "创建用户注册API端点" → 原子级
      - ✅ "实现用户注册API请求参数验证" → 更小的原子级
      - ✅ "实现用户名重复检查API接口" → 原子级
      - ✅ "实现用户密码加密存储逻辑" → 原子级
      - ✅ "实现注册成功返回JWT Token" → 原子级
      - ✅ "添加注册API错误处理和日志记录" → 原子级

   2. **UI开发**：每个UI组件或页面部分都是原子级功能
      - ❌ "实现用户注册页面" → 太大，包含HTML、CSS、JS、验证等
      - ❌ "设计注册表单" → 太大，包含多个输入框和按钮
      - ✅ "创建注册页面HTML结构文件" → 原子级
      - ✅ "添加用户名输入框样式" → 原子级
      - ✅ "实现邮箱格式验证函数" → 原子级
      - ✅ "添加注册按钮点击事件处理" → 原子级
      - ✅ "实现表单提交拦截逻辑" → 原子级
      - ✅ "添加注册成功提示UI组件" → 原子级

   3. **数据库操作**：每个表、字段、索引都是原子级功能
      - ❌ "设计用户数据库" → 太大，包含多个表
      - ❌ "创建用户表" → 太大，包含多个字段和约束
      - ❌ "实现用户数据存储" → 太大，包含验证、加密、存储等多个操作
      - ✅ "创建用户表SQL文件" → 原子级
      - ✅ "添加用户表id字段（主键，自增）" → 原子级
      - ✅ "添加用户表username字段（唯一，非空）" → 原子级
      - ✅ "添加用户表created_at时间戳字段" → 原子级
      - ✅ "创建用户表email索引" → 原子级
      - ✅ "编写用户表创建迁移脚本" → 原子级

   4. **配置和环境**：每个配置项都是原子级功能
      - ❌ "配置项目环境" → 太大，包含多个配置项
      - ❌ "配置数据库连接" → 太大，包含连接池、认证等多个配置
      - ✅ "添加数据库主机配置" → 原子级
      - ✅ "配置数据库端口" → 原子级
      - ✅ "添加数据库用户名和密码" → 原子级
      - ✅ "配置数据库连接池大小" → 原子级
      - ✅ "创建.env环境变量文件" → 原子级
      - ✅ "配置CORS允许的域名" → 原子级

   **非功能性需求集成指南**：
   - 安全性：API包含认证、授权、数据加密
   - 性能：响应时间、并发处理、数据库优化
   - 可靠性：错误处理、重试机制、数据完整性
   - 可维护性：代码注释、文档、日志记录
   - 可扩展性：模块化设计、配置化、插件机制

   **拆分原则（必须遵守！）**：
   - ❌ 当不确定时，继续拆分（拆分过度比拆分不足更好）
   - ✅ 每个功能都要能独立完成（不依赖其他功能的中间状态）
   - ✅ 每个功能都要能独立测试（可以立即验证结果）
   - ✅ 每个功能都要有明确产出（完成后有可见的结果）
   - ✅ 每个功能时间要可控（建议30分钟-2小时内完成）
   - ✅ 每个文件包含1-10个原子级功能
   - ✅ 如果一个文件超过10个原子级任务，继续拆分到子文件

   **完整拆分案例（展示从大到小的拆分过程）**：

   ⚠️ **实战案例库**：完整的拆分案例已移至 `.claude/cases/` 目录

   **使用方法**：
   - Android项目创建 → 参见 `.claude/cases/android-project-creation.md`
   - 基础设施层重构 → 参见 `.claude/cases/` 中的相关案例
   - 其他领域案例 → 根据需求在 `.claude/cases/` 中查找

   **案例文件夹结构**：
   ```
   .claude/cases/
   ├── android-project-creation.md
   ├── infrastructure-refactoring.md
   ├── backend-api-development.md
   └── ...
   ```

   **如何使用案例库**：
   1. 根据用户需求判断项目类型
   2. 查找 `.claude/cases/` 中对应的案例
   3. 参考案例中的拆分规则和原子级标准
   4. 应用到当前需求的功能拆分中

   ⚠️ **重要**：在拆分功能时，务必参考案例库中的实战经验，确保生成真正的原子级功能！

   ❌ **Level 0（太大了 - 用户的原始问题）**：
   ```
   [ ] uc-infrastructure - 基础设施层模块重构
     执行步骤：
     1. 分析uc-framework中的基础设施代码
     2. 识别数据库、缓存、消息队列等基础设施组件
     3. 从uc-framework中抽离基础设施代码
     4. 创建新的uc-infrastructure模块
     5. 迁移相关配置和依赖
     输入要求：
     - uc-framework的源码
     - 数据库配置文件
     - Redis配置文件
     输出预期：
     - 新的uc-infrastructure模块
     - pom.xml配置文件
     - 基础设施组件代码
     注意事项：
     - 保持向后兼容性
     - 不影响现有功能
     - 确保依赖关系正确
     验收标准：
     - 模块可以独立编译
     - 包含所有基础设施组件
     - 通过单元测试
   ```
   ❌ 问题：包含"分析"、"识别"、"抽离"、"迁移"等抽象动作，最终会分析到具体的类和方法，但这个功能本身太抽象

   ❌ **Level 1（仍然太大）**：
   ```
   [ ] 分析uc-framework中的基础设施代码
   [ ] 识别数据库、缓存、消息队列组件
   [ ] 创建uc-infrastructure模块
   [ ] 抽离数据库相关代码
   [ ] 抽离缓存相关代码
   [ ] 抽离消息队列代码
   [ ] 迁移配置文件
   [ ] 更新依赖关系
   ```
   ❌ 问题：每个任务仍然包含抽象动作

   ❌ **Level 2（接近了，但还不够细）**：
   ```
   [ ] 读取uc-framework/pom.xml文件
   [ ] 分析pom.xml中的所有依赖
   [ ] 识别数据库相关依赖
   [ ] 识别缓存相关依赖
   [ ] 识别消息队列相关依赖
   [ ] 创建uc-infrastructure/pom.xml文件
   [ ] 复制数据库相关代码到uc-infrastructure
   [ ] 复制缓存相关代码到uc-infrastructure
   [ ] 复制消息队列代码到uc-infrastructure
   [ ] 更新包名
   [ ] 更新pom.xml依赖
   ```
   ❌ 问题：仍然包含"分析"、"识别"、"复制"等抽象动作，应该到具体的文件、类、方法级别

   ✅ **Level 3（真正的原子级 - 最终必须到达的级别）**：
   ```
   # 数据库组件相关
   [ ] 创建uc-infrastructure/pom.xml文件
   [ ] 在uc-infrastructure/pom.xml中添加<groupId>com.example</groupId>
   [ ] 在uc-infrastructure/pom.xml中添加<artifactId>uc-infrastructure</artifactId>
   [ ] 在uc-infrastructure/pom.xml中添加<version>1.0.0</version>
   [ ] 在uc-infrastructure/pom.xml中添加spring-boot-starter-data-jdbc依赖
   [ ] 在uc-infrastructure/pom.xml中添加mysql-connector-java依赖
   [ ] 创建uc-infrastructure/src/main/java/com/example/infrastructure/db/目录
   [ ] 复制uc-framework/src/main/java/com/example/db/DataSourceConfig.java到uc-infrastructure/src/main/java/com/example/infrastructure/db/
   [ ] 修改DataSourceConfig.java包名从package com.example.db到package com.example.infrastructure.db
   [ ] 在DataSourceConfig.java上添加@ComponentScan注解
   [ ] 创建uc-infrastructure/src/main/java/com/example/infrastructure/db/UserRepository.java文件
   [ ] 在UserRepository.java中添加@Repository注解
   [ ] 在UserRepository.java中添加JdbcTemplate字段
   [ ] 在UserRepository.java中添加构造函数注入JdbcTemplate
   [ ] 在UserRepository.java中添加public User findById(Long id)方法
   [ ] 在UserRepository.java中添加public void save(User user)方法
   [ ] 在UserRepository.java中添加public List<User> findAll()方法

   # 缓存组件相关
   [ ] 在uc-infrastructure/pom.xml中添加spring-boot-starter-cache依赖
   [ ] 在uc-infrastructure/pom.xml中添加redis依赖
   [ ] 创建uc-infrastructure/src/main/java/com/example/infrastructure/cache/目录
   [ ] 复制uc-framework/src/main/java/com/example/cache/RedisConfig.java到uc-infrastructure/src/main/java/com/example/infrastructure/cache/
   [ ] 修改RedisConfig.java包名从package com.example.cache到package com.example.infrastructure.cache
   [ ] 在RedisConfig.java中添加@CacheConfig注解
   [ ] 创建uc-infrastructure/src/main/java/com/example/infrastructure/cache/CacheService.java文件
   [ ] 在CacheService.java中添加@Service注解
   [ ] 在CacheService.java中添加RedisTemplate字段
   [ ] 在CacheService.java中添加构造函数注入RedisTemplate
   [ ] 在CacheService.java中添加public void put(String key, Object value)方法
   [ ] 在CacheService.java中添加public Object get(String key)方法
   [ ] 在CacheService.java中添加public void delete(String key)方法
   [ ] 在CacheService.java中添加public boolean exists(String key)方法

   # 消息队列组件相关
   [ ] 在uc-infrastructure/pom.xml中添加spring-boot-starter-amqp依赖
   [ ] 创建uc-infrastructure/src/main/java/com/example/infrastructure/mq/目录
   [ ] 复制uc-framework/src/main/java/com/example/mq/RabbitMQConfig.java到uc-infrastructure/src/main/java/com/example/infrastructure/mq/
   [ ] 修改RabbitMQConfig.java包名从package com.example.mq到package com.example.infrastructure.mq
   [ ] 创建uc-infrastructure/src/main/java/com/example/infrastructure/mq/MessageProducer.java文件
   [ ] 在MessageProducer.java中添加@Service注解
   [ ] 在MessageProducer.java中添加RabbitTemplate字段
   [ ] 在MessageProducer.java中添加构造函数注入RabbitTemplate
   [ ] 在MessageProducer.java中添加public void send(String queue, Object message)方法
   [ ] 在MessageProducer.java中添加public void sendToExchange(String exchange, String routingKey, Object message)方法
   [ ] 创建uc-infrastructure/src/main/java/com/example/infrastructure/mq/MessageConsumer.java文件
   [ ] 在MessageConsumer.java中添加@Component注解
   [ ] 在MessageConsumer.java中添加@RabbitListener注解
   [ ] 在MessageConsumer.java中添加public void handleMessage(String message)方法

   # 配置迁移
   [ ] 复制uc-framework/src/main/resources/application-database.properties到uc-infrastructure/src/main/resources/
   [ ] 修改application-database.properties中的spring.datasource.username
   [ ] 修改application-database.properties中的spring.datasource.password
   [ ] 创建uc-infrastructure/src/main/resources/application-cache.properties文件
   [ ] 在application-cache.properties中添加spring.redis.host=localhost
   [ ] 在application-cache.properties中添加spring.redis.port=6379
   [ ] 创建uc-infrastructure/src/main/resources/application-mq.properties文件
   [ ] 在application-mq.properties中添加spring.rabbitmq.host=localhost
   [ ] 在application-mq.properties中添加spring.rabbitmq.port=5672

   # 原模块清理
   [ ] 在uc-framework/pom.xml中移除spring-boot-starter-data-jdbc依赖
   [ ] 在uc-framework/pom.xml中移除spring-boot-starter-cache依赖
   [ ] 在uc-framework/pom.xml中移除spring-boot-starter-amqp依赖
   [ ] 删除uc-framework/src/main/java/com/example/db/目录
   [ ] 删除uc-framework/src/main/java/com/example/cache/目录
   [ ] 删除uc-framework/src/main/java/com/example/mq/目录
   [ ] 删除uc-framework/src/main/resources/application-database.properties
   [ ] 在uc-framework/pom.xml中添加uc-infrastructure依赖
   [ ] 在uc-framework/src/main/java/com/example/Application.java中添加@ComponentScan扫描com.example.infrastructure包
   ```
   ✅ 这才是真正的原子级：每个任务都是具体的文件创建、代码行添加、包名修改等，可以立即验证

   **案例1：用户注册功能（完整拆分演示）**

   ❌ **Level 0（太大了）**：
   ```
   [ ] 实现用户注册功能
   ```
   ❌ 问题：包含UI、验证、API、邮件等多个步骤，无法一次性完成

   ❌ **Level 1（仍然太大）**：
   ```
   [ ] 创建用户注册页面
   [ ] 实现注册表单验证
   [ ] 实现注册API
   [ ] 实现注册邮件发送
   ```
   ❌ 问题：每个任务仍然太大，可以继续拆分

   ✅ **Level 2（接近原子级，但可以更细）**：
   ```
   [ ] 创建注册页面HTML结构
   [ ] 设计注册页面CSS样式
   [ ] 实现注册表单验证逻辑
   [ ] 实现用户注册API路由
   [ ] 实现用户名重复检查接口
   [ ] 实现密码加密存储
   [ ] 实现注册成功返回Token
   [ ] 配置邮件服务SMTP
   [ ] 实现注册成功邮件发送
   [ ] 添加注册API日志记录
   ```
   ✅ 好的原子级，但每个还可以更细

   ✅ **Level 3（真正的原子级 - 推荐使用）**：
   ```
   [ ] 创建注册页面HTML文件（register.html）
   [ ] 添加用户名输入框到HTML
   [ ] 添加邮箱输入框到HTML
   [ ] 添加密码输入框到HTML
   [ ] 添加确认密码输入框到HTML
   [ ] 添加注册按钮到HTML
   [ ] 创建注册页面CSS文件（register.css）
   [ ] 设计注册表单容器样式
   [ ] 设计输入框样式
   [ ] 设计按钮样式和悬停效果
   [ ] 实现用户名非空验证
   [ ] 实现用户名长度验证（3-20字符）
   [ ] 实现用户名格式验证（字母数字下划线）
   [ ] 实现邮箱格式验证（正则表达式）
   [ ] 实现密码非空验证
   [ ] 实现密码长度验证（至少8位）
   [ ] 实现密码一致性验证（两次输入一致）
   [ ] 实现前端验证错误提示显示
   [ ] 添加表单提交拦截逻辑
   [ ] 创建注册API路由文件（src/routes/auth.js）
   [ ] 实现用户注册路由处理函数
   [ ] 实现请求体参数解析
   [ ] 实现用户名重复检查数据库查询
   [ ] 实现邮箱重复检查数据库查询
   [ ] 实现密码bcrypt加密（cost=12）
   [ ] 实现用户数据保存到数据库
   [ ] 实现JWT Token生成
   [ ] 实现注册成功响应格式化
   [ ] 实现注册失败错误响应
   [ ] 添加注册API日志记录
   [ ] 创建邮件服务配置文件
   [ ] 设计注册成功邮件HTML模板
   [ ] 实现邮件发送函数
   [ ] 添加邮件发送失败处理
   [ ] 实现邮件发送重试机制
   ```
   ✅ 这才是真正的原子级：每个任务都是单一职责、无法拆分、独立可执行、结果明确

   **案例2：数据库用户表设计（完整拆分演示）**

   ❌ **Level 0（太大了）**：
   ```
   [ ] 设计用户数据库表
   ```

   ✅ **Level 1（接近原子级）**：
   ```
   [ ] 创建用户表SQL文件
   [ ] 添加用户表字段定义
   [ ] 添加用户表索引
   [ ] 编写数据库迁移脚本
   ```

   ✅ **Level 2（真正的原子级）**：
   ```
   [ ] 创建001_create_users_table.sql文件
   [ ] 添加id字段（INT，主键，自增）
   [ ] 添加username字段（VARCHAR(50)，非空，唯一）
   [ ] 添加email字段（VARCHAR(100)，非空，唯一）
   [ ] 添加password_hash字段（VARCHAR(255)，非空）
   [ ] 添加salt字段（VARCHAR(100)，非空）
   [ ] 添加created_at字段（TIMESTAMP，默认CURRENT_TIMESTAMP）
   [ ] 添加updated_at字段（TIMESTAMP，默认CURRENT_TIMESTAMP ON UPDATE）
   [ ] 创建username字段索引
   [ ] 创建email字段索引
   [ ] 创建created_at字段索引
   [ ] 编写001_create_users_table.js迁移脚本
   [ ] 添加数据库连接配置
   [ ] 添加SQL执行逻辑
   [ ] 添加错误处理
   [ ] 添加迁移日志记录
   ```
   ✅ 每个任务都是单一SQL字段或配置项，无法再拆分

   **案例3：前端登录组件（完整拆分演示）**

   ❌ **Level 0（太大了）**：
   ```
   [ ] 实现登录功能
   ```

   ✅ **Level 1（接近原子级）**：
   ```
   [ ] 创建登录页面组件
   [ ] 实现表单验证
   [ ] 实现登录API调用
   [ ] 实现Token存储
   ```

   ✅ **Level 2（真正的原子级）**：
   ```
   [ ] 创建Login.jsx组件文件
   [ ] 导入React和必要hooks
   [ ] 创建登录表单state
   [ ] 创建用户名输入框
   [ ] 创建密码输入框
   [ ] 创建记住登录复选框
   [ ] 创建登录按钮
   [ ] 创建错误提示区域
   [ ] 实现用户名非空验证
   [ ] 实现密码非空验证
   [ ] 实现登录API请求函数
   [ ] 实现请求头配置
   [ ] 实现Token存储到localStorage
   [ ] 实现登录成功跳转逻辑
   [ ] 实现登录失败错误提示
   [ ] 实现表单提交处理函数
   [ ] 添加登录表单CSS样式
   [ ] 实现响应式布局
   [ ] 优化移动端显示
   ```
   ✅ 每个任务都是一个UI元素或一个功能点，无法再拆分

   **验收标准定义**：
   每个原子级功能都必须有明确的验收标准：

   **功能性验收标准**：
   - 功能是否按照需求正确实现？
   - 用户能否成功使用该功能？
   - 功能的输入输出是否符合预期？

   **非功能性验收标准**：
   - 性能：响应时间是否满足要求？
   - 安全：是否有安全漏洞？数据是否加密？
   - 可靠性：错误处理是否完善？是否能稳定运行？
   - 可维护性：代码是否有注释？是否有文档？

   **集成验收标准**：
   - 该功能能否与其他功能正确集成？
   - 接口是否符合规范？
   - 数据传递是否正确？

   **原子级自检清单（生成功能前必须检查！）**：

   在生成每个功能前，问自己以下问题：

   ```
   ✅ 功能清单自检
   ═════════════════════════════════════════

   【执行步骤检查（最关键！）】
   ☐ ⭐ **执行步骤是否只有一行？（最重要！）**
   ☐ 如果执行步骤有多行，必须拆分为多个功能！
   ☐ 是否可以将"执行步骤1"、"执行步骤2"改为独立功能？
   ☐ ❌ 禁止："执行步骤：1. xxx 2. xxx 3. xxx"
   ☐ ✅ 必须："执行步骤：创建xxx文件"

   【单一职责检查】
   ☐ 这个功能是否只做一件事？
   ☐ 这个功能是否只解决一个问题？
   ☐ 如果去掉这个功能，系统是否会缺少某个单一功能？

   【拆分检查】
   ☐ 这个功能可以分解为"先做A，再做B"吗？
   ☐ 如果可以，必须继续拆分！
   ☐ 这个功能涉及多个文件吗？
   ☐ 如果涉及，每个文件一个功能！

   【独立性检查】
   ☐ 这个功能可以独立执行吗？
   ☐ 这个功能需要等待其他功能的中间结果吗？
   ☐ 如果需要，必须拆分或明确依赖关系！

   【产出检查】
   ☐ 完成后有明确、可见的结果吗？
   ☐ 结果是文件、代码、配置还是数据？
   ☐ 如果没有明确产出，必须继续拆分！

   【时间检查】
   ☐ 预估完成时间在30分钟-2小时以内吗？
   ☐ 如果超过，必须继续拆分！

   【测试检查】
   ☐ 这个功能可以立即测试吗？
   ☐ 测试是否需要其他功能配合？
   ☐ 如果需要，必须拆分！

   【验证检查】
   ☐ 有简单的方法验证完成吗？
   ☐ 可以通过"文件存在"、"代码运行"、"测试通过"验证吗？
   ☐ 如果没有，必须继续拆分！

   【连接词检查】
   ☐ 功能描述是否包含"和"、"以及"、"同时"等连接词？
   ☐ 如果包含，说明有多个任务，必须拆分！

   【抽象动词检查（关键！）】
   ☐ 功能描述是否包含"分析"、"识别"、"设计"、"规划"、"研究"等认知类动词？
   ☐ 如果包含，必须拆分到具体的文件、类、方法级别！
   ☐ 功能描述是否包含"抽离"、"迁移"、"重构"、"优化"、"改进"等抽象动作？
   ☐ 如果包含，必须拆分到具体的创建、添加、修改、删除等动作！
   ☐ 功能描述是否涉及"查看"、"读取"、"理解"等探索性动作？
   ☐ 如果包含，必须拆分到具体的文件读取、内容创建等！
   ☐ 功能对象是否是"模块"、"组件"、"系统"、"功能域"等高层级概念？
   ☐ 如果是，必须拆分到具体的文件、类、方法级别！
   ☐ 功能动词是否是具体的（创建、添加、实现、修改、删除、编写）？
   ☐ 如果不是，必须改为具体的动词！

   【最低标准检查（必须满足至少一个！）】
   ☐ ⭐ **文件级别：是否涉及创建/修改/删除一个文件？（最重要）**
   ☐ ⭐ **方法级别：是否涉及实现/修改一个方法？**
   ☐ ❌ **功能模块级别：是否是"用户认证模块"、"用户注册模块"等？（禁止）**
     ⚠️ 如果是，必须继续拆分到文件级别或方法级别！
   ☐ 配置项级别：是否涉及添加/修改一个配置项？
   ☐ 测试级别：是否涉及编写一个测试类或方法？
   ☐ 如果以上都不满足，必须继续拆分！

   ═════════════════════════════════════════
   如果有任何一项检查不通过，必须继续拆分！
   特别是【执行步骤检查】、【抽象动词检查】和【最低标准检查】！

   📌 **两个推荐原子级标准：文件、方法**
   📌 **禁止使用：功能模块级别（太大了）**
   📌 **执行步骤必须只有一行！**
   ```

   **拆分过度与不足的对比**：

   ```
   拆分不足（太大了 - 必须继续拆分）：
   ❌ "实现用户注册功能" - 包含UI、验证、API、邮件等多个文件
   ❌ "创建用户认证模块" - 太大，应拆分为AuthController、AuthService、JwtUtil等文件
   ❌ "实现订单处理模块" - 太大，应拆分为创建订单、支付、发货等文件
   ❌ "用户注册功能模块" - 太大，应拆分为Controller、Service、Validator等文件
   ❌ "uc-infrastructure模块重构" - 包含数据库、缓存、MQ等多个子模块
   结果：Sub-Agent无法完成，会产生幻觉

   拆分过度（太小了 - 可以接受但不推荐）：
   ⚠️ "添加输入框label属性" - 可能过于细碎，属于方法内部细节
   ⚠️ "添加一个CSS注释" - 没有实际功能，属于格式调整
   ⚠️ "调整缩进格式" - 纯格式化，不产生功能
   结果：功能太多，难以管理，但至少不会产生幻觉

   最佳原子级（刚刚好 - 推荐使用）：

   ⭐ **文件级别原子级（最常用）**：
   ✅ "创建AuthController.java文件" - 单一文件
   ✅ "创建AuthService.java文件" - 单一文件
   ✅ "创建JwtUtil.java文件" - 单一文件
   ✅ "创建UserServiceImpl.java文件" - 单一文件
   ✅ "创建register.html文件" - 单一文件
   ✅ "创建register.css文件" - 单一文件
   ✅ "创建register.js文件" - 单一文件
   结果：最常用，最合适，易于管理，可立即验证

   ⭐ **方法级别原子级**：
   ✅ "实现AuthService.loginUser方法" - 单一方法
   ✅ "实现AuthService.registerUser方法" - 单一方法
   ✅ "实现JwtUtil.generateToken方法" - 单一方法
   ✅ "实现JwtUtil.verifyToken方法" - 单一方法
   ✅ "实现Validator.validateEmail方法" - 单一方法
   结果：当文件已存在，只需添加方法时使用

   ⚠️ **功能模块级别（禁止使用 - 太大了）**：
   ❌ "实现用户认证模块" - 包含AuthController、AuthService、JwtUtil等多个文件
   ❌ "实现用户注册功能模块" - 包含Controller、Service、Email、Validator等多个文件
   ❌ "实现订单处理模块" - 包含创建、支付、发货等多个文件
   ❌ "实现基础设施模块" - 包含数据库、缓存、MQ等多个文件
   结果：必须继续拆分到文件级别或方法级别！
   ```

   **原子级拆分的黄金法则**：

   1. **单一职责优先**：一个功能只做一件事
   2. **拆分过度优于不足**：宁可多几个小任务，也不要一个太大任务
   3. **结果导向**：每个任务都要有可见的产出
   4. **时间可控**：每个任务30分钟-2小时内完成
   5. **立即验证**：完成后可以立即测试和检查
   6. **避免"和"字**：功能描述中出现"和"、"以及"就要拆分
   7. **文件级是最佳标准**：优先使用文件级别原子级
   8. **方法级是补充**：当文件已存在，只需添加方法时使用
   9. **禁止功能模块级别**：用户认证模块、用户注册模块等太大，必须继续拆分
   10. **配置项拆分**：每个配置参数都是独立功能
   11. **自检必做**：生成功能前必须通过所有自检项

4. **生成功能列表**：
   - 创建 `.claude/task/main_feature_list.md` 文件
   - **重要**：必须使用用户的原始需求（$ARGUMENTS），不能修改、总结或解释
   - 文件格式：`# 用户原始需求：{$ARGUMENTS}` 后跟功能列表
   - **功能格式**（按层级区分）：

     **主功能/模块级别（非原子级）**：
     ```markdown
     [ ] 模块名称 - 简短描述
     ```
     - ✅ 只需要简单的功能标题
     - ❌ 不需要执行步骤、输入输出等详细信息
     - ❌ 这些是高层概括，会在后续拆分中细化

     **原子级别功能（文件级/方法级）**：
     ```markdown
     [ ] 功能标题
       执行步骤：
       1. 步骤1
       2. 步骤2
       输入要求：
       - 需要的文件、数据、配置等
       输出预期：
       - 应该生成的文件、代码、配置等
       注意事项：
       - 需要避免的问题、限制条件
       验收标准：
       - 如何判断功能完成（可测试的）
     ```
     - ✅ 必须包含详细执行步骤
     - ✅ 必须包含输入输出要求
     - ✅ 必须包含注意事项
     - ✅ 必须包含可测试的验收标准
     - ⚠️ 只有到达原子级别（无法再拆分）时才需要这些详细信息

   - **禁止行为**：
     - ❌ 不能总结用户需求
     - ❌ 不能修改用户需求
     - ❌ 不能解释用户需求
     - ❌ 只能原样记录用户输入的需求
   - **层级说明**：
     - Level 0-1（模块级）：简单标题，无详细信息
     - Level 2+（原子级）：包含完整的执行步骤和验收标准

5. **功能数量**：生成5-15个功能
6. **处理边界情况**：
   - 如果功能超过20项，自动拆分到子文件（使用sub_feature_list_001.md等）
   - 保持功能的可读性和可执行性

7. **多级嵌套拆分（核心优化！）**：
   - 支持无限级嵌套：主文件 → 子文件 → 子子文件 → ...
   - 每个层级都要达到原子级（无法再拆分）
   - 使用缩进或编号表示层级关系
   - 子文件可以继续拆分，直到达到原子级
8. **智能并行执行（使用专业化 Sub-Agent）**：

   **核心原则**：
   - ✅ 使用专业化 Sub-Agent 并行执行无依赖的功能
   - ✅ Sub-Agent 有独立上下文，避免干扰
   - ✅ 自动收集执行总结到 `.claude/feature-execution-summaries/` 目录
   - ✅ 自动生成验证报告检查功能完成情况
   - ✅ 实时更新功能状态

   **Sub-Agent 类型**：
   - **frontend-developer**：前端UI开发（React/Vue/组件/样式）
   - **backend-developer**：后端API开发（RESTful API/业务逻辑）
   - **test-engineer**：测试编写（单元测试/集成测试/E2E测试）
   - **system-architect**：系统架构设计（架构设计/技术选型）
   - **database-expert**：数据库设计（Schema设计/查询优化）
   - **android-developer**：Android应用开发（Kotlin/Java/Android SDK）
   - **miniprogram-developer**：小程序开发（微信/支付宝小程序）
   - **feature-executor**：通用功能执行（其他类型的功能）

   **并行执行示例**：
   ```markdown
   # 场景1：无依赖的模块可以并行
   # 前端和后端可以并行开发

   调用 frontend-developer sub-agent 开发用户注册页面
   调用 backend-developer sub-agent 实现用户注册API
   调用 test-engineer sub-agent 编写用户注册测试

   # 场景2：有依赖的功能必须顺序执行
   # API开发完成后才能进行前端集成

   1. 调用 backend-developer sub-agent 实现API
   2. 等待完成后调用 frontend-developer sub-agent 集成API
   ```

   **判断标准**：
   - ✅ **无依赖** → 可以并行调用多个 Sub-Agent
   - ✅ **有依赖** → 必须按依赖顺序调用
   - ✅ **模型自主判断** → 根据功能描述和依赖关系自动选择 Sub-Agent

   **执行验证检查**：
   - Sub-Agent 完成时自动触发 SubagentStop hook
   - 验证 Sub-Agent 的执行总结是否完整
   - 检查功能状态是否正确更新
   - 识别功能遗漏和状态不一致
   - 生成详细的验证报告到 `.claude/feature-execution-summaries/` 目录
   - 更新验证报告索引 `.claude/feature-execution-summaries/index.md`

9. **用户交互流程（⚠️ 关键约束：必须使用 AskUserQuestion！）**：

   **展示功能列表**：
   - 生成功能列表后，向用户展示
   - 显示完整的功能结构和层级

   ⚠️ **【绝对约束】所有需要与用户交互、询问或确认的情况，必须使用 `AskUserQuestion` 工具！**

   ⚠️ **【禁止行为】**：
   - ❌ 禁止自己猜测用户需求
   - ❌ 禁止自己决定重要参数或配置
   - ❌ 禁止跳过用户确认步骤
   - ❌ 禁止假设用户同意某个方案

   ⚠️ **【必须行为】**：
   - ✅ 必须使用 `AskUserQuestion` 征求用户意见或反馈
   - ✅ 必须使用 `AskUserQuestion` 询问用户需要补充的内容
   - ✅ 必须使用 `AskUserQuestion` 确认用户对某个选择的偏好
   - ✅ 必须使用 `AskUserQuestion` 需要用户提供具体参数或配置
   - ✅ 必须使用 `AskUserQuestion` 询问用户对方案是否满意
   - ✅ 必须使用 `AskUserQuestion` 确认用户是否要继续执行某个步骤
   - ✅ 必须使用 `AskUserQuestion` 任何需要用户输入或决策的场景

   **征求完整性反馈**：
   ⚠️ **必须**使用 `AskUserQuestion` 工具询问用户：
     - "以下功能列表是否完整？是否有遗漏的功能？"
     - "是否有需求需要调整或补充？"
     - "优先级是否正确？"

   **迭代完善**：
   - 根据用户反馈调整功能列表
   - 补充遗漏的功能
   - 调整功能优先级

   **最终确认**：
   ⚠️ **必须**使用 `AskUserQuestion` 工具确认用户是否同意功能列表
   - 用户确认后才生成最终的功能列表文件
   - 询问："功能列表已生成，是否确认开始执行？"

10. **功能执行流程（重要！如何调用 Sub-Agent）**：

    ⚠️ **强制约束**：每个功能必须使用 Sub-Agent 执行，不允许手动执行！

    **第1步：读取功能列表和详细描述**
    - 读取 `.claude/task/main_feature_list.md` 或对应的子文件
    - 找到所有未完成的功能（状态为 `[ ]`）
    - **仔细阅读每个功能的完整描述**：
      - 执行步骤：理解需要做什么
      - 输入要求：准备必要的文件和数据
      - 输出预期：明确应该生成什么
      - 注意事项：避免常见错误
      - 验收标准：确保功能真正完成

    **第2步：确定 Sub-Agent 类型**
    - 根据功能描述和执行步骤判断需要的 Sub-Agent
    - **映射规则**：
      - 前端/UI/组件/样式 → frontend-developer
      - 后端/API/服务器/业务逻辑 → backend-developer
      - 测试/单元测试/集成测试/E2E → test-engineer
      - Android应用/Kotlin/Java → android-developer
      - 小程序/微信/支付宝 → miniprogram-developer
      - 数据库/Schema/查询/索引 → database-expert
      - 架构设计/系统设计/技术选型 → system-architect
      - 其他通用功能 → feature-executor

    **第3步：调用 Sub-Agent（必须！）**
    - ✅ **必须**使用 Sub-Agent 执行，不能跳过
    - ✅ **必须**按照以下语法调用：
      ```
      调用 [sub-agent-name] sub-agent 执行：[功能标题]

      执行要求：
      - 严格按照执行步骤执行
      - 满足输入要求
      - 生成输出预期的内容
      - 注意注意事项
      - 达到验收标准
      ```
    - ✅ **必须**将完整的功能描述传递给 Sub-Agent
    - ✅ Sub-Agent 会独立执行该功能
    - ✅ Sub-Agent 完成后会自动触发验证

    **第4步：Sub-Agent 执行过程**
    - Sub-Agent 读取功能描述
    - 按照执行步骤逐步完成
    - 检查输入要求是否满足
    - 确保输出预期已生成
    - 注意事项中的问题
    - 确认验收标准已达成

    **第5步：更新功能状态**
    - Sub-Agent 完成后，使用 Edit 工具
    - 将功能状态从 `[ ]` 或 `[→]` 改为 `[✓]`
    - 更新 `.claude/task/` 中的相应文件

    **第6步：验证和继续**
    - 等待 SubagentStop hook 验证完成
    - 检查验证报告是否有问题
    - 如果有问题，修正后重新执行
    - 继续下一个功能

    **并行执行示例**：
    ```
    # 无依赖的功能可以并行
    调用 frontend-developer sub-agent 执行：创建登录页面
    执行要求：
    - 按照执行步骤创建HTML、CSS、JS
    - 使用输入要求中的设计规范
    - 生成输出预期的页面文件
    - 注意响应式设计和浏览器兼容性
    - 通过验收标准的所有测试

    调用 backend-developer sub-agent 执行：实现登录API
    执行要求：
    - 按照执行步骤创建路由、控制器、服务
    - 使用输入要求中的数据库连接
    - 生成输出预期的API端点
    - 注意安全性验证和错误处理
    - 通过验收标准的所有测试

    # 有依赖的功能必须顺序执行
    调用 backend-developer sub-agent 执行：实现用户API
    等待完成后
    调用 frontend-developer sub-agent 执行：集成用户API
    ```

    **关键约束（必须遵守！）**：
    - ❌ **禁止**跳过 Sub-Agent 调用手动执行
    - ❌ **禁止**简化或省略功能描述
    - ❌ **禁止**不检查输入输出就完成
    - ❌ **禁止**不验证验收标准
    - ❌ **禁止**在需要用户交互时不使用 AskUserQuestion
    - ✅ **必须**为每个功能调用 Sub-Agent
    - ✅ **必须**传递完整的功能描述
    - ✅ **必须**遵循所有执行步骤
    - ✅ **必须**满足所有输入输出要求
    - ✅ **必须**达到验收标准
    - ✅ **必须**更新功能状态
    - ✅ **必须**在需要用户交互时使用 AskUserQuestion 工具

   ⚠️ **【重要提醒】**：
   - 在执行任何需要用户决策、输入、确认或反馈的步骤之前
   - 在对用户需求有疑问或不确定时
   - 在需要选择技术方案、配置参数或优先级时
   - **必须先使用 AskUserQuestion 工具询问用户，获得明确答复后再继续**

    **避免幻觉的检查清单**：
    - [ ] 是否理解了所有执行步骤？
    - [ ] 是否检查了输入要求？
    - [ ] 是否生成了所有输出预期？
    - [ ] 是否注意了所有注意事项？
    - [ ] 是否通过验收标准测试？
    - [ ] 是否正确更新了功能状态？

## 功能执行规则（重要！）

在生成功能列表时，必须遵守以下执行规则：

### 1. 多级嵌套功能拆分（核心优化！）

#### 嵌套层级结构
支持无限级嵌套，每个层级都可以继续拆分：

```
Level 0: main_feature_list.md (主文件)
    ├── Level 1: sub_user_management.md (用户管理模块)
    │   ├── Level 2: sub_user_auth.md (用户认证子模块)
    │   │   ├── Level 3: sub_user_register.md (用户注册功能)
    │   │   ├── Level 3: sub_user_login.md (用户登录功能)
    │   │   └── Level 3: sub_user_logout.md (用户登出功能)
    │   ├── Level 2: sub_user_profile.md (用户资料子模块)
    │   │   ├── Level 3: sub_user_info.md (用户信息管理)
    │   │   └── Level 3: sub_user_avatar.md (用户头像管理)
    │   └── Level 2: sub_user_permission.md (用户权限子模块)
    │       ├── Level 3: sub_role_management.md (角色管理)
    │       └── Level 3: sub_permission_config.md (权限配置)
    └── Level 1: sub_product_management.md (商品管理模块)
        ├── Level 2: sub_product_category.md (商品分类子模块)
        ├── Level 2: sub_product_info.md (商品信息子模块)
        └── Level 2: sub_product_search.md (商品搜索子模块)
```

#### 嵌套命名规则
- **主文件**：`main_feature_list.md`
- **第一级子文件**：`sub_{module_name}.md`（如 `sub_user_management.md`）
- **第二级子文件**：`sub_{module_name}_{submodule}.md`（如 `sub_user_auth.md`）
- **第三级子文件**：`sub_{module_name}_{submodule}_{feature}.md`（如 `sub_user_auth_register.md`）
- **继续嵌套**：递归添加后缀

#### 嵌套触发条件
- **Level 0 → Level 1**：主文件功能超过20项或需要按模块分组
- **Level 1 → Level 2**：第一级子文件功能超过20项或需要按子模块分组
- **Level 2 → Level 3**：第二级子文件功能超过20项或需要按功能细分
- **继续嵌套**：任何层级都可以继续拆分，直到达到原子级

#### 嵌套文件结构示例

**主文件 (main_feature_list.md)**：
```markdown
# 用户原始需求：{$ARGUMENTS}

[ ] sub_user_management.md - 用户管理模块
[ ] sub_product_management.md - 商品管理模块
[ ] sub_order_management.md - 订单管理模块
[ ] sub_payment_system.md - 支付系统模块
```

**第一级子文件 (sub_user_management.md)**：
```markdown
# 用户管理模块

[ ] sub_user_auth.md - 用户认证子模块
[ ] sub_user_profile.md - 用户资料子模块
[ ] sub_user_permission.md - 用户权限子模块
[ ] sub_user_address.md - 用户地址子模块
```

**第二级子文件 (sub_user_auth.md)**：
```markdown
# 用户认证子模块

[ ] sub_user_auth_register.md - 用户注册功能
[ ] sub_user_auth_login.md - 用户登录功能
[ ] sub_user_auth_logout.md - 用户登出功能
[ ] sub_user_auth_reset_password.md - 密码重置功能
[ ] sub_user_auth_change_password.md - 密码修改功能
[ ] sub_user_auth_verify.md - 身份验证功能
[ ] sub_user_auth_oauth.md - 第三方登录功能
[ ] sub_user_auth_token.md - Token管理功能
[ ] sub_user_auth_session.md - 会话管理功能
[ ] sub_user_auth_security.md - 安全设置功能
```

**第三级子文件 (sub_user_auth_register.md)**：
```markdown
# 用户注册功能（原子级）

[ ] 用户注册页面UI设计
[ ] 注册表单验证逻辑
[ ] 用户名重复检查API
[ ] 邮箱格式验证
[ ] 密码强度检查
[ ] 验证码生成和验证
[ ] 用户数据存储到数据库
[ ] 注册成功后的欢迎邮件
[ ] 注册日志记录
[ ] 注册错误处理和提示
```

#### 原子级判断标准
一个功能是否达到原子级，满足以下条件之一：
- ✅ 无法再进一步拆分（单一职责）
- ✅ 可以独立开发和测试（独立功能）
- ✅ 可以独立部署和运行（独立模块）
- ✅ 有明确的输入和输出（清晰的接口）
- ✅ 不依赖其他同级功能（低耦合）

#### 多级嵌套执行流程
```
第1步：读取 main_feature_list.md
       ↓
第2步：找到所有Level 1子文件（sub_*.md）
       ↓
第3步：按顺序执行Level 1子文件
       ├─ 读取 sub_user_management.md
       ├─ 找到所有Level 2子文件（sub_user_*.md）
       ├─ 按顺序执行Level 2子文件
       │   ├─ 读取 sub_user_auth.md
       │   ├─ 找到所有Level 3子文件（sub_user_auth_*.md）
       │   ├─ 按顺序执行Level 3子文件（原子级功能）
       │   └─ 继续递归执行其他Level 2子文件
       ├─ 继续执行其他Level 1子文件
       ↓
第4步：验证所有功能（包括所有层级）已完成
```

### 2. 主功能和子功能的关系（核心！）

#### 为什么需要子功能文件？
- **触发条件**：当功能列表超过20项时自动创建子文件
- **主功能文件作用**：作为总览文件，包含所有功能的引用
- **子功能文件作用**：存放部分详细功能列表，每文件最多20项

#### 主功能文件 vs 子功能文件

| 特性 | 主功能文件 (main_feature_list.md) | 子功能文件 (sub_feature_list_001.md等) |
|------|----------------------------------|----------------------------------------|
| 位置 | `.claude/task/` 目录 | `.claude/task/` 目录 |
| 作用 | 总览和索引 | 详细功能列表 |
| 内容 | 所有功能的总引用 | 部分功能的详细列表 |
| 数量 | 始终1个 | 根据功能数量，0-N个 |
| 执行顺序 | 最先读取和执行 | 按顺序依次执行 |
| 文件格式 | `# 用户原始需求：...` | `# 子功能列表：...` |

#### 创建逻辑
```
功能数量 ≤ 20项 → 只创建 main_feature_list.md
功能数量 > 20项 → 创建 main_feature_list.md + N个子文件
```

#### 执行逻辑
```
第1步：读取 main_feature_list.md
       ↓
第2步：找到所有子功能文件引用
       ↓
第3步：按顺序执行：
       - main_feature_list.md 中的功能
       - sub_feature_list_001.md 中的功能
       - sub_feature_list_002.md 中的功能
       - ...（依次执行所有子文件）
       ↓
第4步：验证所有功能已完成
```

### 2. 主功能和子功能的关联机制（核心！）

#### 关联方式
- **主文件引用子文件**：主文件通过文件名明确引用子文件
  ```markdown
  [ ] sub_feature_list_001.md - 核心功能模块
  [ ] sub_feature_list_002.md - 高级功能模块
  ```
- **子文件包含具体功能**：每个子文件包含一组相关的详细功能
- **状态同步**：主文件中的引用状态与子文件中的功能状态同步

#### 执行逻辑
```
第1步：读取主文件
       ↓
第2步：找到所有引用的子文件
       ↓
第3步：按顺序执行每个子文件中的所有功能
       - sub_feature_list_001.md（20个功能）
       - sub_feature_list_002.md（3个功能）
       - sub_feature_list_003.md（2个功能）
       ↓
第4步：验证所有功能完成
```

#### 主功能文件处理规则
- **主功能文件**：`main_feature_list.md`
- **子功能文件**：`sub_feature_list_001.md`, `sub_feature_list_002.md` 等
- 执行时必须先读取主功能文件，找到所有引用的子功能文件
- 确保所有功能（包括子文件中的功能）都被完整执行
- 状态同步：主文件引用状态与子文件功能状态保持一致

### 3. 功能执行顺序
- **一个功能一个功能执行**：严格按照列表顺序执行
- **不要跳过功能**：即使是简单的功能也要完整执行

### 4. 状态更新责任（重要！必须执行）

在执行功能的过程中，你**必须**主动更新功能列表中的状态：

#### 状态转换规则
```
[ ]  →  [→]  →  [✓]
(未开始) (进行中) (已完成)
```

#### 何时更新状态
- **开始执行一个功能时**：立即将该功能的 `[ ]` 改为 `[→]`
- **完成一个功能时**：立即将该功能的 `[→]` 改为 `[✓]`
- **开始执行一个子模块时**：立即将该子模块的 `[ ]` 改为 `[→]`
- **完成一个子模块的所有功能时**：立即将该子模块的 `[→]` 改为 `[✓]`

#### 如何更新状态
使用 **Edit 工具** 更新 `.claude/task/` 目录下的所有 `.md` 文件：

**示例1：开始执行注册页面UI**
```python
# 读取 sub_user_register_ui.md
# 找到 [ ] 创建注册页面HTML结构文件
# 使用 Edit 改为 [→] 创建注册页面HTML结构文件
```

**示例2：完成注册页面UI的所有任务**
```python
# 读取 sub_user_register_ui.md
# 确认所有任务都是 [✓]
# 读取 sub_user_auth_register.md
# 找到 [→] sub_user_register_ui.md - 注册页面UI
# 使用 Edit 改为 [✓] sub_user_register_ui.md - 注册页面UI
```

**示例3：完成整个用户注册功能**
```python
# 读取 sub_user_auth_register.md
# 确认所有子模块都是 [✓]
# 读取 sub_user_auth.md
# 找到 [→] sub_user_auth_register.md - 用户注册功能
# 使用 Edit 改为 [✓] sub_user_auth_register.md - 用户注册功能
```

#### 状态更新的重要性
- ✅ **记录进度**：让用户清楚知道哪些功能已完成
- ✅ **避免重复**：防止重复执行已完成的任务
- ✅ **保持同步**：确保子文件和父文件状态一致
- ✅ **提供反馈**：Stop hook会根据状态验证完成情况

#### 状态更新的原则
1. **及时更新**：完成一个任务就立即更新，不要等
2. **准确更新**：确保状态变化准确反映实际进度
3. **完整更新**：不仅更新当前任务，还要更新父级状态
4. **验证更新**：更新后再次检查确认状态正确

### 6. 代码实现规则
- **不要省略任何逻辑**：所有原本的逻辑都要完整实现
- **不要使用批量脚本复制类**：
  - 避免使用 `cp`, `copy` 等命令批量复制类文件
  - 每个类文件都要逐个分析和修改
- **不要因篇幅有限就省略方法实现**：
  - 即使方法很长，也要完整实现
  - 不要注释掉方法实现（`// TODO`, `# ...` 等）
  - 不要使用省略标记

### 6. 功能状态管理
每个功能在执行时必须管理三种状态：

**功能状态格式**：
```markdown
[ ] 功能描述                    # Not started（未开始）
[✓] 功能描述                    # Completed（已完成）
[→] 功能描述                    # In progress（进行中）
```

**状态转换规则**：
- 开始执行功能时：`[ ]` → `[→]`
- 完成功能时：`[→]` → `[✓]`
- 不要跳过任何状态转换

### 7. 完整示例：多级嵌套功能拆分

#### 示例场景：开发完整的电商系统（多级嵌套）

这是一个完整的多级嵌套功能拆分示例，展示了如何将一个复杂系统拆分成原子级功能。

**Level 0: 主文件 (main_feature_list.md)**
```markdown
# 用户原始需求：{$ARGUMENTS}

[ ] sub_user_management.md - 用户管理模块
[ ] sub_product_management.md - 商品管理模块
[ ] sub_order_management.md - 订单管理模块
[ ] sub_payment_system.md - 支付系统模块
[ ] sub_notification_system.md - 通知系统模块
[ ] sub_admin_panel.md - 管理后台模块
[ ] sub_deployment.md - 部署运维模块
```

**Level 1: 用户管理模块 (sub_user_management.md)**
```markdown
# 用户管理模块

[ ] sub_user_auth.md - 用户认证子模块
[ ] sub_user_profile.md - 用户资料子模块
[ ] sub_user_permission.md - 用户权限子模块
[ ] sub_user_address.md - 用户地址子模块
```

**Level 2: 用户认证子模块 (sub_user_auth.md)**
```markdown
# 用户认证子模块

[ ] sub_user_auth_register.md - 用户注册功能
[ ] sub_user_auth_login.md - 用户登录功能
[ ] sub_user_auth_logout.md - 用户登出功能
[ ] sub_user_auth_reset_password.md - 密码重置功能
[ ] sub_user_auth_change_password.md - 密码修改功能
[ ] sub_user_auth_verify.md - 身份验证功能
[ ] sub_user_auth_oauth.md - 第三方登录功能
[ ] sub_user_auth_token.md - Token管理功能
[ ] sub_user_auth_session.md - 会话管理功能
```

**Level 3: 用户注册功能 (sub_user_auth_register.md) - 继续拆分！**

注意：即使是Level 3，如果功能仍然太大，需要继续拆分到Level 4！

❌ **错误的原子级示例**（这些仍然太大）：
```markdown
[ ] 用户注册页面UI设计        # 太大！包含多个步骤
[ ] 注册表单验证逻辑          # 太大！包含多种验证
[ ] 用户数据存储到数据库      # 太大！包含多个操作
```

✅ **正确的原子级示例**（每个都是单一职责）：

**Level 3: 用户注册功能 (sub_user_auth_register.md)**
```markdown
# 用户注册功能（需要继续拆分到Level 4）

[ ] sub_user_register_ui.md - 注册页面UI
[ ] sub_user_register_validation.md - 注册验证逻辑
[ ] sub_user_register_api.md - 注册API接口
[ ] sub_user_register_email.md - 注册邮件发送
```

**Level 4: 注册页面UI (sub_user_register_ui.md) - 真正的原子级**
```markdown
# 注册页面UI（原子级）

[ ] 创建注册页面HTML结构文件
[ ] 设计注册页面CSS样式
[ ] 添加注册页面响应式布局
[ ] 实现注册页面输入框样式
[ ] 添加注册按钮样式和效果
[ ] 实现注册页面加载动画
[ ] 添加注册页面表单提示文本
[ ] 实现注册页面错误提示UI
[ ] 添加注册页面成功提示UI
[ ] 优化注册页面移动端显示
```

**Level 4: 注册验证逻辑 (sub_user_register_validation.md) - 真正的原子级**
```markdown
# 注册验证逻辑（原子级）

[ ] 实现用户名非空验证
[ ] 实现用户名长度验证（3-20字符）
[ ] 实现用户名格式验证（字母数字下划线）
[ ] 实现邮箱格式验证
[ ] 实现密码强度验证（至少8位）
[ ] 实现密码一致性验证（两次输入一致）
[ ] 实现验证码非空验证
[ ] 实现前端验证错误提示显示
[ ] 添加验证表单提交拦截逻辑
```

**Level 4: 注册API接口 (sub_user_register_api.md) - 真正的原子级**
```markdown
# 注册API接口（原子级）

[ ] 创建注册API路由
[ ] 实现用户名重复检查接口
[ ] 实现邮箱重复检查接口
[ ] 实现用户密码加密存储
[ ] 实现用户信息保存到数据库
[ ] 实现注册成功返回Token
[ ] 实现注册失败错误返回
[ ] 添加注册API日志记录
[ ] 实现注册API限流保护
[ ] 添加注册API参数验证
```

**Level 4: 注册邮件发送 (sub_user_register_email.md) - 真正的原子级**
```markdown
# 注册邮件发送（原子级）

[ ] 配置邮件服务SMTP
[ ] 设计注册成功邮件模板
[ ] 实现邮件发送功能
[ ] 添加邮件发送重试机制
[ ] 实现邮件发送失败日志
[ ] 添加邮件发送状态追踪
[ ] 优化邮件内容HTML格式
[ ] 实现邮件批量发送队列
```

**Level 3: 用户登录功能 (sub_user_auth_login.md) - 继续拆分！**
```markdown
# 用户登录功能（需要继续拆分到Level 4）

[ ] sub_user_login_ui.md - 登录页面UI
[ ] sub_user_login_validation.md - 登录验证逻辑
[ ] sub_user_login_api.md - 登录API接口
[ ] sub_user_login_token.md - Token管理
[ ] sub_user_login_session.md - 会话管理
```

**Level 4: 登录页面UI (sub_user_login_ui.md) - 真正的原子级**
```markdown
# 登录页面UI（原子级）

[ ] 创建登录页面HTML结构文件
[ ] 设计登录页面CSS样式
[ ] 添加登录页面响应式布局
[ ] 实现登录表单输入框样式
[ ] 添加登录按钮样式和效果
[ ] 实现记住登录状态UI
[ ] 添加第三方登录按钮样式
[ ] 实现登录页面加载状态
[ ] 添加登录错误提示UI
[ ] 优化登录页面移动端显示
```

**Level 4: 登录验证逻辑 (sub_user_login_validation.md) - 真正的原子级**
```markdown
# 登录验证逻辑（原子级）

[ ] 实现用户名非空验证
[ ] 实现密码非空验证
[ ] 添加输入格式验证
[ ] 实现前端验证错误提示
[ ] 添加验证表单提交拦截
[ ] 实现登录失败计数功能
[ ] 添加账户锁定提示逻辑
```

**Level 4: 登录API接口 (sub_user_login_api.md) - 真正的原子级**
```markdown
# 登录API接口（原子级）

[ ] 创建登录API路由
[ ] 实现用户名密码验证
[ ] 实现登录失败次数限制
[ ] 实现Token生成和返回
[ ] 实现登录成功返回用户信息
[ ] 实现登录失败错误返回
[ ] 添加登录API日志记录
[ ] 实现登录API限流保护
[ ] 添加登录IP地址记录
```

**Level 4: Token管理 (sub_user_login_token.md) - 真正的原子级**
```markdown
# Token管理（原子级）

[ ] 实现JWT Token生成函数
[ ] 实现Token验证中间件
[ ] 实现Token刷新机制
[ ] 实现Token黑名单功能
[ ] 添加Token过期处理
[ ] 实现Token自动续期
```

**Level 4: 会话管理 (sub_user_login_session.md) - 真正的原子级**
```markdown
# 会话管理（原子级）

[ ] 创建用户会话存储表
[ ] 实现会话创建功能
[ ] 实现会话查询功能
[ ] 实现会话更新功能
[ ] 实现会话销毁功能
[ ] 添加会话过期清理
[ ] 实现多设备登录管理
```

#### 执行流程详解

**第1步**：读取 `main_feature_list.md`
- 发现7个模块，按顺序执行

**第2步**：执行用户管理模块
- 读取 `sub_user_management.md`
- 发现4个子模块
- 按顺序执行子模块

**第3步**：执行用户认证子模块
- 读取 `sub_user_auth.md`
- 发现3个功能（注册、登录、登出）
- 按顺序执行功能

**第4步**：执行用户注册功能（原子级）
- 读取 `sub_user_auth_register.md`
- 发现10个原子级任务
- 按顺序执行所有原子级任务
- 完成后标记为 `[✓]`

**第5步**：继续执行其他功能
- 用户登录功能（原子级）
- 用户登出功能（原子级）
- ...

#### 关键优势

1. **无限级嵌套**：可以继续拆分直到达到原子级
2. **清晰的层级**：每个层级都有明确的职责
3. **原子级保证**：最底层都是无法再拆分的原子级功能
4. **灵活扩展**：可以根据需要增加嵌套层级
5. **易于管理**：每个文件只包含相关的功能

#### 如何判断是否需要继续拆分（关键指导！）

**拆分自检清单**：当你生成一个功能时，问自己以下问题：

❌ **必须拆分的信号**：
- 这个功能需要3个或更多步骤来完成？
- 这个功能涉及多个文件或多个组件？
- 这个功能可以分解为"先做A，再做B，再做C"？
- 这个功能需要调用多个API或数据库操作？
- 预估完成时间超过1-2小时？
- 这个功能包含多个不同的职责？

✅ **可以不拆分的信号**：
- 这个功能只是一个单一的文件创建？
- 这个功能只是一个方法或函数的实现？
- 这个功能只是一个简单的配置或修改？
- 这个功能可以立即测试和验证？
- 预估完成时间在1-2小时以内？
- 这个功能只有一个明确的职责？

**实际案例分析**：

**案例1：用户注册功能**
```
❌ 错误的原子级：
[ ] 用户注册功能

✅ 正确的拆分：
[ ] sub_user_register_ui.md - 注册页面UI
[ ] sub_user_register_validation.md - 注册验证逻辑
[ ] sub_user_register_api.md - 注册API接口
[ ] sub_user_register_email.md - 注册邮件发送

继续检查Level 4：
❌ sub_user_register_ui.md 仍然太大：
[ ] 设计注册页面

✅ 拆分到Level 4：
[ ] 创建注册页面HTML结构文件
[ ] 设计注册页面CSS样式
[ ] 添加注册页面响应式布局
[ ] 实现注册页面输入框样式
[ ] 添加注册按钮样式和效果
[ ] 实现注册页面加载动画
[ ] 添加注册页面表单提示文本
[ ] 实现注册页面错误提示UI
[ ] 添加注册页面成功提示UI
[ ] 优化注册页面移动端显示
```

**案例2：数据库设计**
```
❌ 错误的原子级：
[ ] 设计用户数据库

✅ 正确的拆分：
[ ] 创建用户表结构
[ ] 添加用户索引
[ ] 创建用户角色关联表
[ ] 实现数据库迁移脚本
[ ] 配置数据库连接

继续检查每个任务：
❌ 创建用户表结构 仍然太大：
[ ] 创建用户表

✅ 拆分到Level 4：
[ ] 创建用户表SQL文件
[ ] 定义用户表字段结构
[ ] 添加用户表主键
[ ] 创建用户表唯一索引
[ ] 添加用户表时间戳字段
[ ] 编写用户表创建脚本
[ ] 测试用户表创建
```

**案例3：API开发**
```
❌ 错误的原子级：
[ ] 实现用户管理API

✅ 正确的拆分：
[ ] 创建用户列表API
[ ] 创建用户详情API
[ ] 创建用户创建API
[ ] 创建用户更新API
[ ] 创建用户删除API

继续检查每个API：
❌ 创建用户创建API 仍然太大：
[ ] 实现用户创建接口

✅ 拆分到Level 4：
[ ] 创建用户创建路由
[ ] 实现请求参数验证
[ ] 实现用户名重复检查
[ ] 实现密码加密处理
[ ] 实现用户数据保存
[ ] 实现创建成功响应
[ ] 实现创建失败响应
[ ] 添加API日志记录
[ ] 实现API限流保护
```

**拆分决策树**：

```
是否需要拆分？
│
├─ 是 → 这个功能可以分解为多个步骤？
│   │
│   ├─ 是 → 继续拆分
│   │   │
│   │   └─ 重复直到答案为"否"
│   │
│   └─ 否 → 是否涉及多个文件或组件？
│       │
│       ├─ 是 → 继续拆分
│       │
│       └─ 否 → 是否预估超过1-2小时？
│           │
│           ├─ 是 → 继续拆分
│           │
│           └─ 否 → ✅ 这是原子级！
│
└─ 否 → ✅ 这是原子级！
```

**细致化原则总结**：

1. **当不确定时，继续拆分** - 拆分过度比拆分不足更好
2. **每个任务都要能独立完成** - 不依赖其他任务的中间状态
3. **每个任务都要能独立测试** - 可以立即验证结果
4. **每个任务都要有明确产出** - 完成后有可见的结果
5. **每个任务时间要可控** - 建议1-2小时内完成

##### main_feature_list.md (主功能文件 - 模块化设计)
```markdown
# 用户原始需求：{$ARGUMENTS}

[ ] sub_user_management.md - 用户管理模块
[ ] sub_product_management.md - 商品管理模块
[ ] sub_order_management.md - 订单管理模块
[ ] sub_payment_system.md - 支付系统模块
[ ] sub_notification_system.md - 通知系统模块
[ ] sub_admin_panel.md - 管理后台模块
[ ] sub_deployment.md - 部署运维模块
```

**模块化设计原则**：
- ✅ **按业务功能模块分组** - 每个模块对应一个完整的业务功能
- ✅ **模块独立性** - 每个模块可以独立开发和测试
- ✅ **模块完整性** - 每个模块包含所有必需的功能
- ✅ **清晰边界** - 模块之间职责明确，避免重叠

**为什么这样设计？**
- ✅ 业务导向 - 按照实际业务场景组织功能
- ✅ 易于理解 - 开发者清楚每个模块的职责
- ✅ 易于维护 - 修改某个模块不影响其他模块
- ✅ 易于测试 - 可以对每个模块进行独立测试

##### 自动拆分后的文件结构

当功能数量 > 20时，系统会自动创建：

```
.claude/task/
├── main_feature_list.md          # 主文件（总览）
├── sub_feature_list_001.md       # 子文件1（功能1-20）
└── sub_feature_list_002.md       # 子文件2（功能21-25）
```

##### sub_user_management.md (用户管理模块 - 4个功能)
```markdown
# 子功能列表：用户管理模块
## 来源：{$ARGUMENTS}

[ ] 用户注册功能
[→] 用户登录功能
[ ] 密码重置功能
[ ] 用户地址管理
```

**模块职责**：负责所有用户相关的功能，包括注册、登录、密码管理和地址管理

##### sub_product_management.md (商品管理模块 - 5个功能)
```markdown
# 子功能列表：商品管理模块
## 来源：{$ARGUMENTS}

[ ] 商品分类管理
[ ] 商品列表展示
[ ] 商品详情页
[ ] 商品搜索功能
[ ] 商品筛选功能
```

**模块职责**：负责商品展示、搜索和筛选功能

##### sub_order_management.md (订单管理模块 - 4个功能)
```markdown
# 子功能列表：订单管理模块
## 来源：{$ARGUMENTS}

[ ] 购物车管理
[ ] 购物车增删改
[ ] 订单创建
[ ] 订单状态跟踪
```

**模块职责**：负责购物车和订单的完整流程管理

##### sub_payment_system.md (支付系统模块 - 3个功能)
```markdown
# 子功能列表：支付系统模块
## 来源：{$ARGUMENTS}

[ ] 订单支付
[ ] 支付回调处理
[ ] 支付状态同步
```

**模块职责**：负责支付相关的所有功能

##### sub_notification_system.md (通知系统模块 - 3个功能)
```markdown
# 子功能列表：通知系统模块
## 来源：{$ARGUMENTS}

[ ] 邮件通知
[ ] 短信通知
[ ] 站内消息
```

**模块职责**：负责各类通知功能

##### sub_admin_panel.md (管理后台模块 - 3个功能)
```markdown
# 子功能列表：管理后台模块
## 来源：{$ARGUMENTS}

[ ] 管理员登录
[ ] 数据统计分析
[ ] 用户管理
```

**模块职责**：负责管理后台的所有功能

##### sub_deployment.md (部署运维模块 - 3个功能)
```markdown
# 子功能列表：部署运维模块
## 来源：{$ARGUMENTS}

[ ] 性能优化
[ ] 部署上线
[ ] 监控和日志配置
```

**模块职责**：负责部署和运维相关功能

#### 执行流程详解（按模块执行）

**重要：必须按模块完整执行，不要跨模块！**

**第1步**：读取 `main_feature_list.md`
- 系统读取主功能文件
- 发现引用了7个业务模块：
  1. `sub_user_management.md - 用户管理模块`
  2. `sub_product_management.md - 商品管理模块`
  3. `sub_order_management.md - 订单管理模块`
  4. `sub_payment_system.md - 支付系统模块`
  5. `sub_notification_system.md - 通知系统模块`
  6. `sub_admin_panel.md - 管理后台模块`
  7. `sub_deployment.md - 部署运维模块`

**第2步**：按模块顺序执行（关键！）

**模块1：用户管理模块**
- **目标**：完成所有用户相关功能
- **功能数**：4个
- **执行**：
  - 用户注册功能 `[ ]` → `[→]` → `[✓]`
  - 用户登录功能 `[ ]` → `[→]` → `[✓]`
  - 密码重置功能 `[ ]` → `[→]` → `[✓]`
  - 用户地址管理 `[ ]` → `[→]` → `[✓]`
- **模块状态**：完成主文件中 `[ ] sub_user_management.md` → `[✓] sub_user_management.md`

**模块2：商品管理模块**
- **目标**：完成所有商品展示和搜索功能
- **功能数**：5个
- **执行**：
  - 商品分类管理 `[ ]` → `[→]` → `[✓]`
  - 商品列表展示 `[ ]` → `[→]` → `[✓]`
  - 商品详情页 `[ ]` → `[→]` → `[✓]`
  - 商品搜索功能 `[ ]` → `[→]` → `[✓]`
  - 商品筛选功能 `[ ]` → `[→]` → `[✓]`
- **模块状态**：完成主文件中 `[ ] sub_product_management.md` → `[✓] sub_product_management.md`

**模块3：订单管理模块**
- **目标**：完成购物车和订单流程
- **功能数**：4个
- **执行**：
  - 购物车管理 `[ ]` → `[→]` → `[✓]`
  - 购物车增删改 `[ ]` → `[→]` → `[✓]`
  - 订单创建 `[ ]` → `[→]` → `[✓]`
  - 订单状态跟踪 `[ ]` → `[→]` → `[✓]`
- **模块状态**：完成主文件中 `[ ] sub_order_management.md` → `[✓] sub_order_management.md`

**模块4：支付系统模块**
- **目标**：完成支付相关功能
- **功能数**：3个
- **执行**：
  - 订单支付 `[ ]` → `[→]` → `[✓]`
  - 支付回调处理 `[ ]` → `[→]` → `[✓]`
  - 支付状态同步 `[ ]` → `[→]` → `[✓]`
- **模块状态**：完成主文件中 `[ ] sub_payment_system.md` → `[✓] sub_payment_system.md`

**模块5：通知系统模块**
- **目标**：完成所有通知功能
- **功能数**：3个
- **执行**：
  - 邮件通知 `[ ]` → `[→]` → `[✓]`
  - 短信通知 `[ ]` → `[→]` → `[✓]`
  - 站内消息 `[ ]` → `[→]` → `[✓]`
- **模块状态**：完成主文件中 `[ ] sub_notification_system.md` → `[✓] sub_notification_system.md`

**模块6：管理后台模块**
- **目标**：完成管理后台功能
- **功能数**：3个
- **执行**：
  - 管理员登录 `[ ]` → `[→]` → `[✓]`
  - 数据统计分析 `[ ]` → `[→]` → `[✓]`
  - 用户管理 `[ ]` → `[→]` → `[✓]`
- **模块状态**：完成主文件中 `[ ] sub_admin_panel.md` → `[✓] sub_admin_panel.md`

**模块7：部署运维模块**
- **目标**：完成部署和运维
- **功能数**：3个
- **执行**：
  - 性能优化 `[ ]` → `[→]` → `[✓]`
  - 部署上线 `[ ]` → `[→]` → `[✓]`
  - 监控和日志配置 `[ ]` → `[→]` → `[✓]`
- **模块状态**：完成主文件中 `[ ] sub_deployment.md` → `[✓] sub_deployment.md`

**第3步**：验证所有模块
- 系统统计：
  - 模块总数：7个
  - 已完成模块：7个
  - 每个模块的功能数：
    - 用户管理：4个
    - 商品管理：5个
    - 订单管理：4个
    - 支付系统：3个
    - 通知系统：3个
    - 管理后台：3个
    - 部署运维：3个
  - 总功能数：25个
  - 已完成功能：25个
  - 未完成功能：0个

**关键提醒**：
- ✅ 必须按模块完整执行，不要跳过模块
- ✅ 一个模块完成后才能开始下一个模块
- ✅ 模块内部的功能也要按顺序执行
- ✅ 状态同步：子文件功能状态 ↔ 主文件模块状态

#### 关键点说明（模块化执行）

1. **模块化分组（核心！）**：
   - ✅ 按业务功能模块分组，不是简单的编号分组
   - ✅ 每个模块对应一个完整的业务功能
   - ✅ 模块之间职责明确，避免功能重叠
   - ✅ 示例：用户管理模块、商品管理模块、订单管理模块

2. **模块完整性**：
   - ✅ 每个模块包含所有必需的功能
   - ✅ 模块内部功能按顺序执行
   - ✅ 一个模块完成后才能开始下一个模块
   - ✅ 不允许跨模块执行（比如商品模块未完成不能做支付模块）

3. **模块独立性**：
   - ✅ 每个模块可以独立开发和测试
   - ✅ 修改某个模块不影响其他模块
   - ✅ 易于理解每个模块的职责和边界
   - ✅ 便于团队分工协作

4. **状态同步机制**：
   - 子文件中：功能状态 `[ ]` → `[→]` → `[✓]`
   - 主文件中：模块状态同步更新
   - 模块开始执行：主文件中 `[ ] sub_user_management.md` → `[→] sub_user_management.md`
   - 模块全部完成：主文件中 `[→] sub_user_management.md` → `[✓] sub_user_management.md`

5. **执行顺序**：
   - 必须严格按照主文件中的模块顺序执行
   - 用户管理 → 商品管理 → 订单管理 → 支付系统 → 通知系统 → 管理后台 → 部署运维
   - 每个模块的功能也要按顺序执行

### 7. 简单示例（功能 ≤ 20项）

如果功能不超过20项，只创建主文件，直接列出功能：

```markdown
# 用户原始需求：{$ARGUMENTS}

[ ] 分析现有认证系统的代码结构
  执行步骤：
  1. 读取现有认证相关代码文件
  2. 识别使用的认证库和框架
  3. 分析当前的token管理方式
  4. 检查密码存储方式
  5. 评估会话管理机制
  输入要求：
  - 访问项目代码仓库
  - 读取现有认证代码
  输出预期：
  - 认证系统分析报告
  - 识别出的问题清单
  注意事项：
  - 不要遗漏任何认证相关代码
  - 注意安全性问题
  - 考虑性能影响
  验收标准：
  - 完成所有代码文件分析
  - 生成详细的分析报告
  - 识别出至少5个改进点

[→] 识别可以改进的设计模式
  执行步骤：
  1. 分析当前架构的问题
  2. 研究现代认证最佳实践
  3. 识别可以应用的设计模式
  4. 评估每种模式的优缺点
  5. 推荐最合适的方案
  输入要求：
  - 前一步的分析报告
  - 项目技术栈信息
  输出预期：
  - 设计模式改进建议
  - 每种模式的适用性分析
  注意事项：
  - 考虑项目复杂度
  - 评估学习成本
  - 确保向后兼容
  验收标准：
  - 识别出至少3个设计模式
  - 每个模式都有详细分析
  - 提供明确的推荐方案

[ ] 设计新的认证架构
  执行步骤：
  1. 设计整体架构图
  2. 定义API端点规范
  3. 设计数据库表结构
  4. 规划token管理流程
  5. 设计错误处理机制
  输入要求：
  - 前一步的设计模式建议
  - 项目需求文档
  输出预期：
  - 完整的架构设计文档
  - API规范文档
  - 数据库设计文档
  注意事项：
  - 确保架构可扩展
  - 考虑安全性和性能
  - 提供清晰的实施步骤
  验收标准：
  - 架构图清晰完整
  - API规范符合RESTful原则
  - 数据库设计合理

[ ] 实现JWT token管理
  执行步骤：
  1. 选择JWT库（推荐 jsonwebtoken）
  2. 实现token生成函数
  3. 实现token验证中间件
  4. 实现token刷新机制
  5. 实现token黑名单
  输入要求：
  - 前一步的API规范
  - 项目依赖信息
  输出预期：
  - src/utils/jwt.js（JWT工具函数）
  - src/middlewares/auth.js（认证中间件）
  - 测试文件
  注意事项：
  - 确保token安全性
  - 正确处理过期时间
  - 避免token泄漏
  验收标准：
  - 可以成功生成token
  - 可以验证token有效性
  - token刷新机制正常工作
  黑名单功能正常

[ ] 添加OAuth 2.0支持
  执行步骤：
  1. 研究OAuth 2.0流程
  2. 选择OAuth库（推荐 passport）
  3. 配置OAuth提供商
  4. 实现授权回调
  5. 实现用户信息获取
  输入要求：
  - OAuth提供商的API密钥
  - 前一步的API规范
  输出预期：
  - OAuth配置文件
  - 授权路由和回调
  - 用户信息处理逻辑
  注意事项：
  - 保护OAuth密钥安全
  - 处理各种错误情况
  - 支持多个OAuth提供商
  验收标准：
  - 可以成功授权
  - 可以获取用户信息
  - 错误处理完善

[ ] 实现密码加密和盐值处理
  执行步骤：
  1. 选择加密算法（推荐 bcrypt）
  2. 实现密码加密函数
  3. 实现密码验证函数
  4. 生成随机盐值
  5. 更新用户注册/登录逻辑
  输入要求：
  - 用户模型定义
  - 加密库信息
  输出预期：
  - 密码加密工具函数
  - 更新后的用户服务
  - 测试用例
  注意事项：
  - 使用足够的加密强度
  - 确保盐值随机性
  - 避免常见密码错误
  验收标准：
  - 密码正确加密存储
  - 可以验证密码正确性
  - 加密强度符合安全标准

[ ] 添加双因素认证（2FA）
  执行步骤：
  1. 选择2FA方案（TOTP）
  2. 集成2FA库（推荐 speakeasy）
  3. 实现2FA QR码生成
  4. 实现2FA验证逻辑
  5. 实现2FA恢复码
  输入要求：
  - 用户模型扩展
  - 2FA库文档
  输出预期：
  - 2FA服务模块
  - 2FA相关API端点
  - 前端2FA界面
  注意事项：
  - 确保QR码安全性
  - 生成安全的恢复码
  - 提供清晰的设置流程
  验收标准：
  - 可以生成2FA QR码
  - 可以验证2FA码
  - 恢复码可以正常使用

[ ] 实现会话管理
  执行步骤：
  1. 设计会话存储方案
  2. 实现会话创建
  3. 实现会话查询
  4. 实现会话更新
  5. 实现会话销毁
  输入要求：
  - Redis或数据库配置
  - 会话管理需求
  输出预期：
  - 会话管理服务
  - 会话相关API
  - 会话中间件
  注意事项：
  - 确保会话安全性
  - 实现会话过期机制
  - 支持多设备登录管理
  验收标准：
  - 会话可以正常创建
  - 会话可以正常查询
  - 会话过期正常工作
  可以销毁指定会话

[ ] 编写单元测试
  执行步骤：
  1. 识别需要测试的函数
  2. 编写测试用例
  3. 测试正常情况
  4. 测试异常情况
  5. 达到80%以上覆盖率
  输入要求：
  - 前一步实现的所有代码
  - 测试框架配置
  输出预期：
  - tests/auth.test.js
  - tests/jwt.test.js
  - tests/oauth.test.js
  注意事项：
  - 测试要独立可重复
  - 覆盖所有边界情况
  - 使用mock隔离依赖
  验收标准：
  - 测试覆盖率≥80%
  - 所有测试通过
  - 测试运行时间合理

[ ] 集成测试
  执行步骤：
  1. 编写端到端测试用例
  2. 测试完整注册流程
  3. 测试完整登录流程
  4. 测试OAuth登录流程
  5. 测试2FA流程
  输入要求：
  - 所有实现的API
  - 测试环境配置
  输出预期：
  - tests/integration/auth-flow.test.js
  - 测试报告
  注意事项：
  - 使用真实的数据库
  - 测试数据要隔离
  - 清理测试数据
  验收标准：
  - 所有测试场景通过
  - 测试报告详细
  - 无性能问题

[ ] 更新API文档
  执行步骤：
  1. 使用Swagger生成API文档
  2. 添加认证相关API
  3. 添加OAuth API
  4. 添加2FA API
  5. 添加示例代码
  输入要求：
  - 所有API端点
  - Swagger配置
  输出预期：
  - docs/api/swagger.yaml
  - 可交互的API文档
  注意事项：
  - 文档要准确完整
  - 提供清晰的示例
  - 包含错误码说明
  验收标准：
  - 所有API都有文档
  - 示例代码可运行
  - 文档格式正确

[ ] 迁移现有用户数据
  执行步骤：
  1. 分析现有用户数据
  2. 编写迁移脚本
  3. 测试迁移脚本
  4. 执行数据迁移
  5. 验证迁移结果
  输入要求：
  - 现有数据库
  - 用户数据表结构
  输出预期：
  - migrations/update_auth.js
  - 迁移日志
  - 验证报告
  注意事项：
  - 确保数据安全
  - 提供回滚方案
  - 记录所有变更
  验收标准：
  - 所有用户数据正确迁移
  - 密码正确加密
  - 无数据丢失

[ ] 性能测试和优化
  执行步骤：
  1. 设计性能测试用例
  2. 测试认证API性能
  3. 识别性能瓶颈
  4. 实施优化措施
  5. 验证优化效果
  输入要求：
  - 性能测试工具
  - 优化方案
  输出预期：
  - 性能测试报告
  - 优化建议
  - 优化后的代码
  注意事项：
  - 模拟真实负载
  - 关注响应时间
  - 监控资源使用
  验收标准：
  - 认证API响应时间<200ms
  - 支持并发1000+
  - 资源使用合理

[ ] 部署到生产环境
  执行步骤：
  1. 准备生产环境
  2. 配置环境变量
  3. 部署代码
  4. 执行数据库迁移
  5. 验证部署结果
  输入要求：
  - 生产服务器
  - 部署脚本
  输出预期：
  - 生产环境部署
  - 部署日志
  - 验证报告
  注意事项：
  - 确保零停机部署
  - 备份现有数据
  - 监控部署过程
  验收标准：
  - 部署成功无错误
  - 所有功能正常
  - 性能符合预期

[ ] 监控和日志配置
  执行步骤：
  1. 配置应用日志
  2. 集成监控工具
  3. 设置告警规则
  4. 配置日志分析
  5. 测试监控告警
  输入要求：
  - 监控工具配置
  - 告警规则定义
  输出预期：
  - 日志配置文件
  - 监控仪表板
  - 告警规则
  注意事项：
  - 确保日志格式统一
  - 设置合理的告警阈值
  - 定期检查日志
  验收标准：
  - 日志正常记录
  - 告警及时触发
  - 监控数据准确
```

**注意**：这个例子只有15个功能，没有超过20项限制，因此：
- ✅ 只创建 `main_feature_list.md`
- ✅ 主文件直接列出所有功能（包含详细描述）
- ✅ 没有子文件
- ✅ 执行时直接按顺序执行主文件中的功能
- ✅ 每个功能都有详细的执行步骤、输入输出、注意事项和验收标准

## 输出格式

```markdown
# 用户原始需求：{用户的原始描述}

[ ] 功能标题1
  执行步骤：
  1. 步骤1
  2. 步骤2
  输入要求：
  - 需要的文件、数据、配置等
  输出预期：
  - 应该生成的文件、代码、配置等
  注意事项：
  - 需要避免的问题、限制条件
  验收标准：
  - 如何判断功能完成（可测试的）

[ ] 功能标题2
  执行步骤：
  1. 步骤1
  2. 步骤2
  输入要求：
  - 需要的文件、数据、配置等
  输出预期：
  - 应该生成的文件、代码、配置等
  注意事项：
  - 需要避免的问题、限制条件
  验收标准：
  - 如何判断功能完成（可测试的）
...
```

## 注意事项

- **必须**使用 `[ ]` 作为功能状态标记
- **必须**为每个功能包含完整的详细描述
- **必须**确保功能之间有逻辑顺序
- **必须**避免跳过执行步骤或简化描述
- **必须**包含可测试的验收标准

⚠️ **【绝对约束：AskUserQuestion 使用规则】**

- **必须**在需要用户交互时使用 `AskUserQuestion` 工具
- **禁止**直接假设或猜测用户需求
- **禁止**自己决定重要参数或配置
- **禁止**跳过用户确认步骤
- **必须**主动询问用户，而不是自己决策
- **必须**使用 `AskUserQuestion` 获取用户偏好、确认、输入等信息

⚠️ **【何时必须使用 AskUserQuestion】**（所有以下情况必须使用，不能跳过）：
1. ✅ 征求用户意见或反馈
2. ✅ 询问用户需要补充的内容
3. ✅ 确认用户对某个选择的偏好
4. ✅ 需要用户提供具体参数或配置
5. ✅ 询问用户对方案是否满意
6. ✅ 确认用户是否要继续执行某个步骤
7. ✅ 任何需要用户输入或决策的场景

⚠️ **【何时不要使用 AskUserQuestion】**：
1. ❌ 当信息可以从文件或代码中读取时
2. ❌ 当有明确的标准答案时
3. ❌ 当不需要用户输入就能完成任务时
4. ❌ 当已经从用户需求中明确说明时

- 如果无法生成功能列表，使用fallback模板（根据需求类型选择重构/开发/测试/优化等模板）

### AskUserQuestion 使用约束（⚠️ 绝对重要！）

⚠️ **【核心原则】**：当有疑问时，总是使用 AskUserQuestion 工具！

⚠️ **【何时必须使用 AskUserQuestion】**（以下情况必须使用，不能跳过）：
1. ✅ 征求用户意见或反馈
2. ✅ 询问用户需要补充的内容
3. ✅ 确认用户对某个选择的偏好
4. ✅ 需要用户提供具体参数或配置
5. ✅ 询问用户对方案是否满意
6. ✅ 确认用户是否要继续执行某个步骤
7. ✅ 任何需要用户输入或决策的场景
8. ✅ 对用户需求有疑问或不确定时
9. ✅ 需要选择技术方案、配置参数或优先级时

⚠️ **【何时不要使用 AskUserQuestion】**：
1. ❌ 当信息可以从文件或代码中读取时
2. ❌ 当有明确的标准答案时
3. ❌ 当不需要用户输入就能完成任务时
4. ❌ 当已经从用户需求中明确说明时

⚠️ **【AskUserQuestion 使用示例】**：

**示例1：询问用户是否同意功能列表**
```markdown
功能列表已生成，共包含15个原子级功能。

⚠️ **必须**使用 AskUserQuestion 工具询问：
"功能列表已生成，共包含15个原子级功能。
请确认是否同意这个列表？是否需要调整？"

用户确认后才能生成文件。
```

**示例2：确认技术选型**
```markdown
⚠️ **必须**使用 AskUserQuestion 工具询问：
"数据库方案需要选择：MySQL 还是 PostgreSQL？
请根据你的项目需求选择。"

根据用户选择继续。
```

**示例3：获取用户偏好**
```markdown
⚠️ **必须**使用 AskUserQuestion 工具询问：
"是否需要支持第三方登录（Google、GitHub等）？
请选择：[是/否]"
```

**示例4：确认执行顺序**
```markdown
⚠️ **必须**使用 AskUserQuestion 工具询问：
"功能列表已按以下优先级排序：
1. 用户认证模块
2. 商品管理模块
3. 订单管理模块
请确认是否需要调整优先级？"
```

**示例5：获取具体参数**
```markdown
⚠️ **必须**使用 AskUserQuestion 工具询问：
"请输入数据库连接信息：
- 数据库主机地址：
- 数据库端口：
- 数据库名称：
- 用户名：
- 密码："
```

**示例6：验证需求理解**
```markdown
⚠️ **必须**使用 AskUserQuestion 工具询问：
"我理解您的需求是：
1. 实现用户注册功能
2. 实现用户登录功能
3. 实现密码重置功能
我的理解是否正确？是否遗漏了其他功能？"
```

⚠️ **【关键提醒】**：
- **不要害怕提问**：问清楚比做错更好
- **不要假设用户想法**：用户可能想得和你不一样
- **不要自己决定重要参数**：让用户自己决定
- **不要跳过确认步骤**：确认可以避免返工
- **使用 AskUserQuestion 获取用户明确的答复，然后严格按照用户答复执行**

## Fallback模板

如果无法生成合适的功能列表，使用以下模板之一：

**重构类功能**：
```
[ ] 读取并分析现有代码结构
[ ] 理解业务需求和逻辑
[ ] 设计新的架构方案
[ ] 实现核心功能模块
[ ] 迁移和重构代码
[ ] 处理依赖和配置
[ ] 测试验证功能
[ ] 编写文档
```

**开发类功能**：
```
[ ] 分析需求和功能点
[ ] 设计系统架构
[ ] 创建项目结构
[ ] 实现核心功能
[ ] 实现用户界面
[ ] 添加测试用例
[ ] 配置和部署
[ ] 编写使用文档
```

**测试类功能**：
```
[ ] 理解测试范围
[ ] 分析现有代码
[ ] 设计测试方案
[ ] 编写测试用例
[ ] 执行测试
[ ] 验证功能完整性
[ ] 记录测试结果
[ ] 生成测试报告
```

**优化类功能**：
```
[ ] 性能分析
[ ] 识别瓶颈
[ ] 优化代码
[ ] 验证改进
[ ] 文档更新
```

## 实战经验总结（基于奥特曼卡牌PK Android项目）

### 关键发现

从奥特曼卡牌PK案例中发现，即使看起来是"创建xxx文件"的功能，如果执行步骤包含多个不同的文件或配置，这个功能就太大了，必须拆分。

### 核心改进点

**1. 执行步骤必须拆分**
- ❌ 错误：`[ ] 创建Android项目基础结构` → 执行步骤有4个不同的配置
- ✅ 正确：将每个执行步骤独立为一个功能
  `[ ] 创建build.gradle文件`
  `[ ] 在build.gradle中添加CameraX依赖`
  `[ ] 在build.gradle中添加OCR依赖`
  `[ ] 在AndroidManifest.xml中添加相机权限`
  `[ ] 在AndroidManifest.xml中添加存储权限`

**2. 功能标题必须具体化**
- ❌ 错误：`[ ] 配置build.gradle添加必要依赖`
- ✅ 正确：`[ ] 在build.gradle中添加CameraX依赖`
  （每个依赖一个功能，而不是"必要依赖"这种模糊表述）

**3. 配置项拆分到最细粒度**
- ❌ 错误：`[ ] 配置AndroidManifest.xml` → 包含多个权限和Activity
- ✅ 正确：每个权限和每个Activity注册独立为一个功能
  `[ ] 在AndroidManifest.xml中添加相机权限`
  `[ ] 在AndroidManifest.xml中添加存储权限`
  `[ ] 在AndroidManifest.xml中注册UploadActivity`

**4. 测试必须拆分**
- ❌ 错误：`[ ] 编写单元测试（核心业务逻辑）` → 包含多个测试类
- ✅ 正确：每个测试类独立为一个功能
  `[ ] 编写UploadActivity单元测试`
  `[ ] 编写BattleEngine单元测试`
  `[ ] 编写OCRService单元测试`

### 实战标准

**Android开发原子级标准**：
```
✅ 创建XXX.java文件（单一文件）
✅ 在build.gradle中添加XXX依赖（单一依赖）
✅ 在AndroidManifest.xml中添加XXX权限（单一权限）
✅ 在AndroidManifest.xml中注册XXX Activity（单一Activity）
✅ 实现XXX类YYY方法（单一方法）
✅ 在XXX类中添加ZZZ字段（单一字段）
✅ 创建activity_xxx.xml布局文件（单一布局文件）
```

**禁止使用的模式**：
```
❌ "创建Android项目结构" → 包含多个目录和文件
❌ "配置build.gradle" → 包含多个依赖
❌ "配置AndroidManifest.xml" → 包含多个权限和Activity
❌ "编写单元测试" → 包含多个测试类
❌ "实现用户认证模块" → 包含多个文件
```

现在请根据用户的需求生成功能列表并创建文件。

⚠️ **【最后提醒】**：
- 在整个功能生成和执行过程中
- 如果有**任何**疑问、不确定或需要用户决策的情况
- **必须先使用 AskUserQuestion 工具询问用户**
- 获得用户明确答复后，再严格按照答复执行
- **不要自己猜测或假设用户的需求或偏好**
