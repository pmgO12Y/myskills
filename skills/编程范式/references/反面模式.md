# 函数式编程反面模式

本文档列出在代码审查和重构中需要识别和避免的常见反面模式。这些模式违背了函数式编程的核心原则。

---

## 1. 可变状态与重新赋值

**问题描述**：在创建后修改数据，或使用可变变量存储状态。

**反例**：

```javascript
// 可变变量
let count = 0;
function increment() {
  count++; // 修改了外部状态
  return count;
}

// 修改传入的对象
function updateUser(user, newName) {
  user.name = newName; // 直接修改了参数！
  return user;
}

// 可变数组操作
const numbers = [1, 2, 3];
numbers.push(4); // 修改了原数组
```

**正确做法**：

```javascript
// 使用 const，状态通过参数和返回值传递
const increment = count => count + 1;

// 返回新对象
const updateUser = (user, newName) => ({ ...user, name: newName });

// 返回新数组
const addNumber = (numbers, n) => [...numbers, n];
```

**审查要点**：
- 检查 `let` / `var` 的使用，大部分场景应替换为 `const`
- 检查对对象属性和数组方法的直接修改（`.push`、`.splice`、`.pop`、属性赋值等）
- 检查函数是否修改了传入的参数

---

## 2. 副作用泄漏到业务逻辑

**问题描述**：核心业务逻辑函数中混杂了 I/O、状态更新等副作用。

**反例**：

```javascript
function getDiscountedPrice(product, user) {
  const discount = fetchUserDiscount(user.id); // 网络请求！
  logEvent('price_calculated', { productId: product.id }); // I/O
  return product.price * (1 - discount);
}
```

**正确做法**：

```javascript
// 纯函数：只负责计算
const getDiscountedPrice = (price, discount) =>
  price * (1 - discount);

// 副作用在调用方或专门的 effect 层处理
async function displayPrice(product, user) {
  const discount = await fetchUserDiscount(user.id);
  const price = getDiscountedPrice(product.price, discount);
  logEvent('price_calculated', { productId: product.id });
  return price;
}
```

**审查要点**：
- 检查函数内部是否有 HTTP 请求、数据库查询、文件读写
- 检查是否调用了 `console.log` 或全局日志对象
- 检查是否修改了全局状态或 DOM
- 将纯逻辑提取到独立的纯函数中

---

## 3. 命令式循环

**问题描述**：使用 `for`、`while`、`do...while` 手动遍历集合，而非声明式的高阶函数。

**反例**：

```javascript
const names = [];
for (let i = 0; i < users.length; i++) {
  if (users[i].age >= 18) {
    names.push(users[i].name.toUpperCase());
  }
}
```

**正确做法**：

```javascript
const names = users
  .filter(u => u.age >= 18)
  .map(u => u.name.toUpperCase());
```

**例外情况**：
- 需要提前终止并返回的场景（但 `find`、`some`、`every` 通常可替代）
- 性能极度敏感的底层代码（大部分业务代码不属于此类）
- 需要维护复杂索引的状态机（应考虑重构为递归或状态模式）

**审查要点**：
- 检查所有 `for`、`while` 循环
- 判断是否可以替换为 `map`、`filter`、`reduce`、`find`、`some`、`every`、`flatMap`
- 嵌套循环考虑 `flatMap` 或递归

---

## 4. Null / Undefined 的滥用

**问题描述**：使用 `null`、`undefined`、裸指针或隐式空值表示"不存在"，导致空指针异常和防御性代码蔓延。

**反例**：

```javascript
function getUserName(userId) {
  const user = db.find(userId);
  if (user) {           // 防御性检查
    if (user.profile) { // 又一层检查
      return user.profile.name;
    }
  }
  return null;          // 继续传播 null
}

// 调用方又需要防御
const name = getUserName(1);
if (name) {
  console.log(name.toUpperCase());
}
```

**正确做法**：

```javascript
// 使用 Option/Maybe 类型显式处理缺失
const getUserName = (userId) => {
  const user = db.find(userId);
  return user.flatMap(u => u.profile).map(p => p.name);
};

// 或提供默认值
const name = getUserName(1).getOrElse('Anonymous');
```

**审查要点**：
- 检查函数是否返回 `null` / `undefined` 表示失败或不存在
- 检查代码中是否有大量嵌套的防御性 null 检查
- 推荐使用 Optional/Maybe 类型、默认值模式或空对象模式

---

## 5. 深层嵌套的条件语句

**问题描述**：多层 `if/else` 嵌套导致代码难以阅读和推理。

**反例**：

```javascript
function processOrder(order) {
  if (order) {
    if (order.items) {
      if (order.items.length > 0) {
        if (order.user) {
          if (order.user.isActive) {
            return calculateTotal(order);
          } else {
            return 'User inactive';
          }
        } else {
          return 'No user';
        }
      } else {
        return 'Empty cart';
      }
    } else {
      return 'No items';
    }
  } else {
    return 'No order';
  }
}
```

**正确做法**：

```javascript
const processOrder = (order) =>
  pipe(
    validateExists,
    validateHasItems,
    validateHasUser,
    validateUserActive,
    calculateTotal
  )(order);

const validateExists = (order) =>
  order ? ok(order) : err('No order');

const validateHasItems = (order) =>
  order.items?.length > 0 ? ok(order) : err('Empty cart');

// ... 以此类推
```

**审查要点**：
- 检查超过 2-3 层的嵌套条件
- 使用卫语句（guard clauses）提前返回
- 使用 Result/Option 类型链式处理错误
- 将复杂条件提取为命名良好的谓词函数

---

## 6. 隐式依赖与全局状态

**问题描述**：函数依赖于未在参数中显式传入的状态，导致难以测试和推理。

**反例**：

```javascript
// 隐式依赖全局配置
function calculateShipping(address) {
  if (config.freeShippingEnabled && address.country === 'US') {
    return 0;
  }
  return config.baseShippingRate;
}

// 隐式依赖单例
function getCurrentUser() {
  return AuthService.getInstance().currentUser;
}
```

**正确做法**：

```javascript
// 所有依赖通过参数传入
const calculateShipping = (config, address) =>
  config.freeShippingEnabled && address.country === 'US'
    ? 0
    : config.baseShippingRate;

// 纯函数不隐藏依赖
const getCurrentUser = (authService) => authService.currentUser;
```

**审查要点**：
- 检查函数是否读取全局变量、模块级变量或单例
- 检查是否使用了隐式的 `this` 上下文传递状态
- 将依赖提取为参数，使用依赖注入或 Reader Monad 模式

---

## 7. 函数嵌套地狱（Callback / Pyramid of Doom）

**问题描述**：深层嵌套的函数调用或回调，导致代码难以阅读。

**反例**：

```javascript
getUser(userId, (err, user) => {
  if (err) return handleError(err);
  getOrders(user.id, (err, orders) => {
    if (err) return handleError(err);
    processOrders(orders, (err, result) => {
      if (err) return handleError(err);
      saveResult(result, (err) => {
        if (err) return handleError(err);
        sendNotification(user, result);
      });
    });
  });
});
```

**正确做法**：

```javascript
// 使用 Promise / async-await 或函数组合
const processUserOrders = pipe(
  getUser,
  chain(getOrders),
  chain(processOrders),
  chain(saveResult),
  map(result => tap(sendNotification)(result))
);
```

**审查要点**：
- 检查深层嵌套的回调或条件
- 使用 Promise、async/await、函数组合或 Monad 链式调用替代

---

## 8. 过度使用类与继承

**问题描述**：使用类和继承来组织代码，导致紧耦合和隐式状态。

**反例**：

```javascript
class DiscountCalculator {
  constructor(user) {
    this.user = user; // 隐式状态
  }

  calculate(price) {
    if (this.user.isVIP) {
      return price * 0.8;
    }
    return price;
  }
}
```

**正确做法**：

```javascript
// 纯函数替代类方法
const calculateDiscount = (user, price) =>
  user.isVIP ? price * 0.8 : price;

// 数据 + 行为分离：数据是数据，函数是函数
const user = { name: 'Alice', isVIP: true };
const discountedPrice = calculateDiscount(user, 100);
```

**审查要点**：
- 检查类是否仅用于存储数据（应使用 record/struct/对象字面量）
- 检查类方法是否可以提取为独立纯函数
- 检查继承层次是否可以替换为组合
- 避免在类中维护可变内部状态

---

## 9. 过早优化与性能偏执

**问题描述**：为了想象中的性能问题而拒绝使用函数式模式，导致代码更难维护。

**常见误区**：
- "创建新数组/对象太慢，我要复用旧的" — 现代引擎对短期对象的优化非常好
- "map/filter 比 for 循环慢" — 在绝大多数业务代码中差异可以忽略不计
- "递归会栈溢出" — 使用尾递归优化，或在浅层递归中完全安全

**实践指导**：
- 先用清晰、正确的函数式风格编写代码
- 在性能成为实际问题后再优化
- 对于大数据量，考虑惰性求值（generator、stream、lazy list）

---

## 审查检查清单

在审查代码时，检查以下反面模式：

- [ ] 是否存在对变量、对象或数组的重新赋值？
- [ ] 函数是否修改了传入的参数？
- [ ] 业务逻辑中是否混杂了 I/O 或副作用？
- [ ] 是否使用了 `for` / `while` 循环（而非声明式操作）？
- [ ] 是否返回或传递了 `null` / `undefined`？
- [ ] 条件嵌套是否超过 2-3 层？
- [ ] 函数是否依赖了未在签名中声明的全局/隐式状态？
- [ ] 是否使用了深层嵌套的回调或调用链？
- [ ] 类是否仅用于包裹一组纯函数？
- [ ] 是否为了想象中的性能问题而牺牲了代码清晰度？
