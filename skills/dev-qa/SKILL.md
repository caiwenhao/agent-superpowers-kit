---
name: dev-qa
description: |
  全面测试：启动前后端服务，浏览器测试 + 接口验证 + 日志分析 + 数据库检查。
  发现问题自动修复并重新验证，循环直到全部通过。
  Use when: "测试", "QA", "全面测试", "test everything",
  "run qa", "跑一下测试", "验证功能"
argument-hint: "[测试 URL 或服务启动说明]"
---

# /dev-qa - 全面测试 + 自动修复

启动前后端服务，进行浏览器测试 + 接口验证 + 日志分析 + 数据库检查。
发现问题自动修复，循环直到全部通过。

## 输入

<test_context> #$ARGUMENTS </test_context>

## 流程

### Step 1: 确认测试环境

检查项目配置文件（CLAUDE.md, package.json, Makefile, docker-compose.yml 等），
自动检测前后端启动命令、测试 URL、日志路径。

如果无法自动检测，用 AskUserQuestion 询问：
> 请提供以下信息：
> - 前端启动命令（如 `npm run dev`）
> - 后端启动命令（如 `go run main.go`）
> - 测试 URL（如 `http://localhost:3000`）
> - 数据库类型和连接方式（如有）

### Step 2: 启动服务

使用 Step 1 检测到的启动命令，在后台启动前端和后端服务。

要求：
- 将日志重定向到固定路径（如 `/tmp/dev-backend.log`、`/tmp/dev-frontend.log`）
- 将 PID 写入 PID 文件（如 `/tmp/dev-backend.pid`、`/tmp/dev-frontend.pid`）
- 等待服务就绪（通过 health check URL 或端口探测确认）

根据项目实际技术栈（Go/Python/Node 等）生成对应的启动命令，不要套用固定模板。

### Step 3: 全面测试

并行执行以下测试：

#### 3a. 浏览器测试 (gstack-qa)

使用 Skill tool 调用 `gstack-qa`，进行浏览器端测试：
- 页面渲染验证
- 交互功能测试
- UI 回归检查
- 发现问题自动修复

#### 3b. 接口验证 (Superpowers)

使用 Agent tool 启动 `compound-engineering:workflow:bug-reproduction-validator` (Superpower)：
- 验证 API 接口的请求/响应
- 检查错误处理
- 验证边界条件

#### 3c. 日志分析

使用 Grep 工具（而非 bash grep）检查服务运行日志：
- 搜索 `/tmp/dev-backend.log` 和 `/tmp/dev-frontend.log` 中的 error/panic/warning/fatal
- 分析异常堆栈信息

#### 3d. 数据库检查（如适用）

检查数据库状态：
- 表结构是否正确
- 数据完整性
- migration 是否成功

### Step 4: 问题修复循环

如果任何测试发现问题：
1. 汇总所有问题
2. 自动修复代码
3. 重启服务
4. 重新运行失败的测试
5. 循环直到全部通过（最多 5 轮）

5 轮后如果仍有问题，用 AskUserQuestion：
> 已完成 5 轮测试修复循环，仍有 {N} 个未解决的问题：
> {问题列表}
>
> - A) 继续修复（再开 5 轮）
> - B) 忽略剩余问题，继续进入验收
> - C) 中断，回到编码阶段手动处理

### Step 5: 停止服务 + 输出

测试全部通过后：
1. 从 PID 文件读取 PID，停止后台服务
2. 清理临时日志和 PID 文件
3. 输出测试结果总结

告诉用户：

> 全面测试通过。
> - 浏览器测试: {N} 项通过
> - 接口验证: {N} 项通过
> - 日志检查: 无异常
> - 数据库检查: 正常
>
> 下一步：
> - `/dev-accept` - 进入人工验收
