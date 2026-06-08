# skills/

此目錄用於存放本專案的 Agent skills（例如：特定任務的提示詞、工具編排、工作流腳本或可重用的協作規範）。

## 目錄約定

- 每個 skill 建議獨立一個子資料夾（以 skill 名稱命名）
- 每個 skill 至少包含：
  - README.md（用途、輸入/輸出、使用方式）
  - prompts/（如有）
  - workflows/（如有）

## 變更守門

- 新增或修改 skills/ 下內容時，需同步更新：
  - README.md 的文件導覽（若對團隊日常工作流有影響）
  - AGENTS.md（若引入新的協作角色或流程）

