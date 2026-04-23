# 函数式编程核心原则

本文档定义函数式编程（Functional Programming, FP）的核心原则。在处理任何与函数式编程相关的代码审查、编写或重构任务时，加载并遵循这些原则。

---

## 1. 纯函数（Pure Functions）

纯函数是函数式编程的基石。

**定义**：给定相同的输入，永远返回相同的输出，且不会产生任何可观察的副作用。

**特征**：
- 输出仅依赖于输入参数
- 不读取或修改函数外部的状态
- 不执行 I/O 操作（网络请求、文件读写、打印日志等）
- 不修改传入的参数

**示例对比**：

```javascript
// 不纯：依赖外部状态
let taxRate = 0.2;
function calculateTax(amount) {
  return amount * taxRate; // 依赖外部变量
}

// 纯：所有依赖都通过参数传入
function calculateTax(amount, taxRate) {
  return amount * taxRate;
}
```

**实践指导**：
- 尽可能将外部依赖提取为参数
- 使用依赖注入而非全局状态
- 将不纯操作隔离到特定的函数边界

---

## 2. 不可变性（Immutability）

数据一旦创建，就不应被修改。

**定义**：避免在创建后修改数据。任何变更都通过创建新的数据副本来实现。

**特征**：
- 变量赋值后不再重新赋值（使用 `const` 而非 `let`/`var`）
- 对象和数组不直接修改，而是创建新实例
- 状态更新返回新状态，而非修改原状态

**示例对比**：

```javascript
// 可变
function addItem(cart, item) {
  cart.items.push(item); // 修改了原数组
  return cart;
}

// 不可变
function addItem(cart, item) {
  return {
    ...cart,
    items: [...cart.items, item]
  };
}
```

**实践指导**：
- 默认使用 `const`（JS/TS）或等价常量声明
- 使用展开运算符（`...`）、切片、拼接等创建副本
- 对于深层嵌套结构，使用结构共享或不可变数据结构库
- 在面向对象语言中，使对象字段为 `final`/`readonly`

---

## 3. 无副作用（No Side Effects）

副作用是纯函数的对立面。

**定义**：副作用是指函数在执行过程中对外部世界产生的任何可观察的变化。

**常见的副作用**：
- 修改全局变量或外部状态
- 修改传入的参数（尤其是引用类型）
- 发起 HTTP 请求或数据库操作
- 读写文件
- 操作 DOM
- 打印日志到控制台
- 抛出异常（有争议，但通常视为副作用）
- 读取当前时间、随机数等不确定值

**副作用隔离策略**：
- 将业务逻辑（纯函数）与副作用分离
- 将副作用集中到系统边界（如 MVC 中的 Controller、Effect 层）
- 使用 IO Monad / Effect 系统来显式标记副作用（如 Haskell、Effect-TS）

**分层架构示例**：

```
┌─────────────────────────────────────┐
│           Effect Layer              │  ← 副作用（I/O、状态更新）
│  (Impure: API calls, DB writes)     │
├─────────────────────────────────────┤
│           Business Logic            │  ← 纯函数（计算、转换）
│  (Pure: transformations, validation)│
├─────────────────────────────────────┤
│           Data Layer                │  ← 不可变数据结构
│  (Immutable state, domain models)   │
└─────────────────────────────────────┘
```

---

## 4. 一等函数与高阶函数（First-Class & Higher-Order Functions）

函数作为一等公民是函数式编程的重要特征。

**一等函数**：函数可以像值一样被传递、赋值、存储和返回。

**高阶函数**：接受函数作为参数或返回函数的函数。

**常见的高阶函数模式**：
- `map` — 将每个元素转换为新值
- `filter` — 根据条件筛选元素
- `reduce` / `fold` — 将集合归约为单个值
- `compose` / `pipe` — 组合多个函数
- `curry` / `partial` — 部分应用和柯里化

**示例**：

```javascript
const users = [{ name: 'Alice', age: 30 }, { name: 'Bob', age: 25 }];

// 高阶函数：map、filter、reduce
const adultNames = users
  .filter(u => u.age >= 18)  // filter 接受一个谓词函数
  .map(u => u.name);          // map 接受一个转换函数

// 函数组合
const pipe = (...fns) => x => fns.reduce((v, f) => f(v), x);
const getAdultNames = pipe(
  arr => arr.filter(u => u.age >= 18),
  arr => arr.map(u => u.name)
);
```

---

## 5. 函数组合与管道（Function Composition & Piping）

将简单函数组合成复杂逻辑，而非嵌套调用。

**定义**：函数组合是将多个函数串联起来，使一个函数的输出成为下一个函数的输入。

**两种风格**：
- **Compose**：从右到左执行 `compose(f, g, h)(x) = f(g(h(x)))`
- **Pipe**：从左到右执行 `pipe(h, g, f)(x) = f(g(h(x)))`

**示例对比**：

```javascript
// 嵌套调用（难以阅读）
const result = formatCurrency(calculateDiscount(getPrice(product)));

// 管道（线性阅读）
const getFinalPrice = pipe(getPrice, calculateDiscount, formatCurrency);
const result = getFinalPrice(product);
```

**实践指导**：
- 优先将复杂逻辑拆分为小的、单一的纯函数
- 使用组合来表达数据流，而非嵌套
- 每个组合步骤应具有清晰的单一职责

---

## 6. 声明式编程（Declarative over Imperative）

描述"做什么"而非"怎么做"。

**定义**：声明式代码关注结果和意图，命令式代码关注执行步骤和状态变更。

**对比**：

```javascript
// 命令式：告诉计算机如何一步步做
function getActiveUserNames(users) {
  const names = [];
  for (let i = 0; i < users.length; i++) {
    if (users[i].active) {
      names.push(users[i].name);
    }
  }
  return names;
}

// 声明式：描述想要的结果
const getActiveUserNames = users =>
  users.filter(u => u.active).map(u => u.name);
```

**实践指导**：
- 使用高阶函数（map/filter/reduce）替代手动循环
- 使用表达式替代语句
- 将控制流抽象为组合模式

---

## 7. 引用透明性（Referential Transparency）

表达式可被其值替换而不影响程序行为。

**定义**：如果一个表达式在程序中所有出现的位置都可以被它的计算结果替换，而不会改变程序的行为，那么这个表达式就是引用透明的。

**推论**：
- 纯函数天然具有引用透明性
- 支持等价推理：如果 `f(x) = y`，那么所有 `f(x)` 出现的地方都可以替换为 `y`
- 使代码更易于测试、缓存和并行化

**示例**：

```javascript
// 引用透明
const double = x => x * 2;
// double(5) 可以安全地被替换为 10

// 不透明：因为每次结果不同
const now = () => new Date().toISOString();
// now() 不能被替换为固定字符串
```

---

## 8. 递归（Recursion）

使用递归替代显式循环。

**定义**：函数调用自身来解决问题。

**尾递归优化**：当递归调用是函数最后一个操作时，某些编译器可以优化为迭代，避免栈溢出。

**示例对比**：

```javascript
// 命令式循环
function sum(arr) {
  let total = 0;
  for (let i = 0; i < arr.length; i++) {
    total += arr[i];
  }
  return total;
}

// 递归
function sum(arr) {
  if (arr.length === 0) return 0;
  return arr[0] + sum(arr.slice(1));
}

// 尾递归
function sum(arr, acc = 0) {
  if (arr.length === 0) return acc;
  return sum(arr.slice(1), acc + arr[0]);
}
```

**实践指导**：
- 在支持尾递归优化的语言中，优先使用尾递归
- 对于不支持尾递归的语言（如大多数 JS 引擎），递归深度较大时仍可使用 reduce 等安全的高阶函数
- 递归特别适合处理树形结构和分治算法

---

## 9. 类型系统与代数数据类型（Type System & ADTs）

使用类型系统增强函数式代码的表达力和安全性。

**代数数据类型（ADTs）**：
- **积类型（Product Types）**：`struct` / `record` — 同时拥有多个值（与关系）
- **和类型（Sum Types）**：`enum` / `union` / `sealed` — 多个可能性中取其一（或关系）

**Option/Maybe 类型**：
显式表达"可能有值也可能没有"，替代 `null` / `undefined`。

```typescript
type Option<T> = { _tag: 'Some'; value: T } | { _tag: 'None' };

function findUser(id: string): Option<User> {
  const user = db.get(id);
  return user ? { _tag: 'Some', value: user } : { _tag: 'None' };
}
```

**Result/Either 类型**：
显式表达操作可能失败，替代异常抛出。

```typescript
type Result<T, E> = { _tag: 'Ok'; value: T } | { _tag: 'Err'; error: E };

function parseNumber(str: string): Result<number, string> {
  const n = Number(str);
  return isNaN(n) ? { _tag: 'Err', error: 'Invalid number' } : { _tag: 'Ok', value: n };
}
```

**实践指导**：
- 让无效状态在类型层面无法表示
- 使用类型系统来强制处理边界情况
- 避免使用 `null`，改用 Option/Maybe
- 避免使用异常控制流，改用 Result/Either

---

## 总结检查清单

在处理代码时，检查以下原则是否得到遵守：

- [ ] 函数是否只依赖其参数？（纯函数）
- [ ] 数据是否未被修改，而是创建了新的数据？（不可变性）
- [ ] 函数是否避免了修改外部状态或执行 I/O？（无副作用）
- [ ] 是否使用了 map/filter/reduce 等声明式操作替代手动循环？（声明式）
- [ ] 复杂逻辑是否由小的、单一职责的函数组合而成？（组合）
- [ ] 是否避免了 null/undefined 的传递？（类型安全）
- [ ] 表达式是否可以被其结果安全替换？（引用透明）
