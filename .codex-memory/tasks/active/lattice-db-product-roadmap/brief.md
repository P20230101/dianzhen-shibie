<!-- codex-memory:template=task-brief:v1 -->

# 任务简报
## 目标

- 建立 `dianzhen shujuku` 项目的长期产品路线与研发路线治理入口。
- 将 `2026-04-21` 定义为 `M0 可控开发启动验收`。
- 让后续开发能一眼看清：项目在做什么、当前阶段是什么、哪些任务可新开支线、哪些任务必须同支线推进。

## 范围 / 不做

- 做：
  - 长期目标
  - 阶段路线
  - 明天验收视图
  - 分支拆分策略
  - 长期任务记忆
- 不做：
  - 业务功能实现
  - 自动化脚本
  - UI
  - 全量数据导入

## 当前状态
- 已完成：
  - 项目目录骨架
  - schema / mapping v1
  - `dispatch/tasks` 调度体系
  - 任务启动规范
- 进行中：
  - 项目长期路线治理设计
  - M0 验收视图设计
  - 分支策略标注设计
- 未开始：
  - `tasks/project-overview.md`
  - `tasks/roadmap.md`
  - `tasks/branch-strategy.md`
  - 首条真实任务按新规范跑通

## 已确认决定
- 详见 `decisions.md`

## 关键索引

- 详见 `refs.md`

## 风险 / 下一步
- 风险：
  - 首次真实任务尚未按新规范跑通
  - `2026-04-21` 验收以后仍需用真实任务验证可操作性
- 下一步：
  - 评审本轮 design spec
  - 生成 implementation plan
  - 实现总览文件与长期任务记忆入口
