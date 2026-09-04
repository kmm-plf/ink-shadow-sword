# 你需要给Token添加的权限

## 当前Token权限 (读取)
✅ repo（仓库）
✅ codespace（codespaces只读）

## 缺少权限
❌ codespaces（codespaces读写）← 关键！

## 操作步骤

### 方法1：生成新的Fine-grained Token（推荐）
1. 打开: https://github.com/settings/tokens
2. 点击 **Generate new token (classic)**
3. Token名称: `AI Movie Maker`
4. 过期时间: 选任意
5. 勾选以下 **scopes**:
   - ✅ `repo` (全量)
   - ✅ `codespaces` (读写)
   - ✅ `workflow` (可选)
6. 点击 **Generate token**
7. **复制新token给我**

### 方法2：如果已经是Classic Token
1. 打开: https://github.com/settings/tokens
2. 找到包含 `ghp_GamfmtaU...` 的token
3. 点击 **Edit** 旁边的三点菜单
4. 检查是否勾选了 `codespaces` scope
5. 如果没有，重新生成一个

---

## 同时，我在准备开发环境配置
我会先创建好 .devcontainer.json，你给新token后立刻开始干活。