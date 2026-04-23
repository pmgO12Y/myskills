# 函数式重构模式

本文档提供将命令式/面向对象代码重构为函数式风格的具体模式和步骤。

---

## 模式 1：将命令式循环替换为高阶函数

### 场景
代码使用 `for` 或 `while` 循环遍历集合并执行转换、筛选或聚合。

### 重构步骤

1. 识别循环的意图：是映射（一对一转换）、筛选（过滤）、还是归约（聚合）？
2. 用对应的声明式方法替换循环
3. 将循环体提取为纯函数（如果逻辑较复杂）

### 映射（Map）

```javascript
// 重构前
const upperNames = [];
for (let i = 0; i < users.length; i++) {
  upperNames.push(users[i].name.toUpperCase());
}

// 重构后
const upperNames = users.map(u => u.name.toUpperCase());
```

### 筛选（Filter）

```javascript
// 重构前
const adults = [];
for (let i = 0; i < users.length; i++) {
  if (users[i].age >= 18) {
    adults.push(users[i]);
  }
}

// 重构后
const adults = users.filter(u => u.age >= 18);
```

### 组合映射与筛选

```javascript
// 重构前
const names = [];
for (let i = 0; i < users.length; i++) {
  if (users[i].active) {
    names.push(users[i].name);
  }
}

// 重构后
const names = users.filter(u => u.active).map(u => u.name);
// 或惰性求值：users.flatMap(u => u.active ? [u.name] : [])
```

### 归约（Reduce / Fold）

```javascript
// 重构前
let total = 0;
for (let i = 0; i < orders.length; i++) {
  total += orders[i].amount;
}

// 重构后
const total = orders.reduce((sum, o) => sum + o.amount, 0);
```

### 分组（GroupBy）

```javascript
// 重构前
const byCategory = {};
for (let i = 0; i < products.length; i++) {
  const cat = products[i].category;
  if (!byCategory[cat]) byCategory[cat] = [];
  byCategory[cat].push(products[i]);
}

// 重构后
const byCategory = products.reduce((acc, p) => ({
  ...acc,
  [p.category]: [...(acc[p.category] || []), p]
}), {});
// 或使用 groupBy 工具函数
```

### 查找（Find / Some / Every）

```javascript
// 重构前
let found = null;
for (let i = 0; i < users.length; i++) {
  if (users[i].id === targetId) {
    found = users[i];
    break;
  }
}

// 重构后
const found = users.find(u => u.id === targetId);
```

---

## 模式 2：提取纯函数

### 场景
函数混杂了计算逻辑和副作用，或函数过长、职责过多。

### 重构步骤

1. 识别函数中的纯逻辑部分（只依赖输入、只返回结果）
2. 将纯逻辑提取为独立的纯函数
3. 在原函数中调用提取的纯函数，副作用保留在调用层

### 示例

```javascript
// 重构前
function submitOrder(cart, user) {
  let total = 0;
  for (const item of cart.items) {
    total += item.price * item.quantity;
  }
  
  if (user.isVIP) {
    total *= 0.9;
  }
  
  const order = {
    userId: user.id,
    items: cart.items,
    total,
    createdAt: new Date()
  };
  
  db.orders.insert(order); // 副作用
  sendEmail(user.email, 'Order placed'); // 副作用
  return order;
}

// 重构后
// 纯函数：计算总价
const calculateTotal = (items, isVIP) => {
  const subtotal = items.reduce((sum, item) =>
    sum + item.price * item.quantity, 0);
  return isVIP ? subtotal * 0.9 : subtotal;
};

// 纯函数：构建订单对象
const buildOrder = (cart, user, total, now) => ({
  userId: user.id,
  items: cart.items,
  total,
  createdAt: now
});

// 不纯函数：协调副作用
async function submitOrder(cart, user) {
  const total = calculateTotal(cart.items, user.isVIP);
  const now = new Date(); // 副作用：读取当前时间
  const order = buildOrder(cart, user, total, now);
  
  await db.orders.insert(order);
  await sendEmail(user.email, 'Order placed');
  return order;
}
```

---

## 模式 3：用不可变数据替代可变对象/数组

### 场景
代码直接修改对象属性或数组元素。

### 重构步骤

1. 识别所有可变修改点
2. 使用对应语言的不可变更新语法创建新实例
3. 对于深层嵌套，考虑使用 Lens 模式或不可变库

### 对象更新

```javascript
// 重构前
function updateAddress(user, newAddress) {
  user.address.street = newAddress.street;
  user.address.city = newAddress.city;
  return user;
}

// 重构后
const updateAddress = (user, newAddress) => ({
  ...user,
  address: { ...user.address, ...newAddress }
});
```

### 数组更新（指定索引）

```javascript
// 重构前
function updateItem(items, index, newItem) {
  items[index] = newItem;
  return items;
}

// 重构后
const updateItem = (items, index, newItem) =>
  items.map((item, i) => i === index ? newItem : item);
```

### 数组插入/删除

```javascript
// 重构前
function removeItem(items, index) {
  items.splice(index, 1);
  return items;
}

// 重构后
const removeItem = (items, index) =>
  [...items.slice(0, index), ...items.slice(index + 1)];
```

### 深层嵌套更新

```javascript
// 重构前
function updateUserEmail(users, userId, newEmail) {
  const user = users.find(u => u.id === userId);
  if (user) {
    user.contact.email = newEmail;
  }
  return users;
}

// 重构后（手动展开）
const updateUserEmail = (users, userId, newEmail) =>
  users.map(u => u.id === userId
    ? { ...u, contact: { ...u.contact, email: newEmail } }
    : u
  );

// 或使用 Lens 模式（借助库如 monocle-ts、ramda 等）
```

---

## 模式 4：用函数组合替代嵌套调用

### 场景
函数调用层层嵌套，难以阅读。

### 重构步骤

1. 识别嵌套调用链
2. 将每一步提取为命名函数
3. 使用 `pipe` 或 `compose` 组合

### 示例

```javascript
// 重构前
const result = formatCurrency(
  applyTax(
    calculateDiscount(
      getPrice(product),
      user.discountRate
    ),
    taxRate
  )
);

// 重构后
const getFinalPrice = pipe(
  p => getPrice(p),
  price => calculateDiscount(price, user.discountRate),
  discounted => applyTax(discounted, taxRate),
  formatCurrency
);

const result = getFinalPrice(product);
```

### 组合谓词函数

```javascript
// 重构前
const isValidUser = user =>
  user && user.age >= 18 && user.email && user.isActive;

// 重构后
const isNotNull = x => x !== null && x !== undefined;
const isAdult = u => u.age >= 18;
const hasEmail = u => !!u.email;
const isActive = u => u.isActive;

const isValidUser = allPass([isNotNull, isAdult, hasEmail, isActive]);
```

---

## 模式 5：用 Optional/Maybe 替代 Null 检查

### 场景
代码中充斥着 `if (x !== null)` 等防御性检查。

### 重构步骤

1. 识别所有可能返回 `null` / `undefined` 的函数
2. 将返回值包装为 Option/Maybe 类型
3. 使用 `map`、`flatMap`、`getOrElse` 等方法处理链式操作

### 示例

```javascript
// 重构前
function getStreetAddress(userId) {
  const user = findUser(userId);
  if (user) {
    const address = user.address;
    if (address) {
      const street = address.street;
      if (street) {
        return street.trim();
      }
    }
  }
  return 'Unknown';
}

// 重构后（使用自定义 Option）
const getStreetAddress = (userId) =>
  findUser(userId)
    .flatMap(u => u.address)
    .flatMap(a => a.street)
    .map(s => s.trim())
    .getOrElse('Unknown');

// 或使用可选链 + 空值合并（语言原生支持时）
const getStreetAddress = (userId) =>
  findUser(userId)?.address?.street?.trim() ?? 'Unknown';
```

---

## 模式 6：用 Result/Either 替代异常控制流

### 场景
使用 `try/catch` 控制正常业务逻辑流。

### 重构步骤

1. 识别用于业务逻辑流的异常抛出
2. 将可能失败的操作返回 `Result<T, E>` 类型
3. 使用 `map`、`flatMap`、`mapError` 等组合结果

### 示例

```javascript
// 重构前
function divide(a, b) {
  if (b === 0) throw new Error('Division by zero');
  return a / b;
}

try {
  const result = divide(10, 0);
  console.log(result);
} catch (e) {
  console.error(e.message);
}

// 重构后
type Result<T, E> = Ok<T> | Err<E>;

const divide = (a, b) =>
  b === 0
    ? err('Division by zero')
    : ok(a / b);

divide(10, 0)
  .map(r => console.log(r))
  .mapError(e => console.error(e));
```

---

## 模式 7：将类重构为数据 + 函数

### 场景
类仅用于封装数据和操作数据的方法。

### 重构步骤

1. 将类的字段提取为 record/struct/接口定义
2. 将类方法提取为独立的纯函数，接受数据作为首参数
3. 使用组合替代继承

### 示例

```javascript
// 重构前
class Rectangle {
  constructor(width, height) {
    this.width = width;
    this.height = height;
  }
  area() { return this.width * this.height; }
  perimeter() { return 2 * (this.width + this.height); }
  scale(factor) {
    this.width *= factor;  // 可变的！
    this.height *= factor;
    return this;
  }
}

// 重构后
// 数据定义
const Rectangle = (width, height) => ({ width, height });

// 纯函数
const area = r => r.width * r.height;
const perimeter = r => 2 * (r.width + r.height);
const scale = (r, factor) => ({
  width: r.width * factor,
  height: r.height * factor
});

// 使用
const rect = Rectangle(10, 20);
const scaled = scale(rect, 2);
console.log(area(scaled)); // 400
console.log(area(rect));   // 200（原对象未被修改）
```

---

## 模式 8：用惰性求值优化性能

### 场景
处理大量数据或无限序列时，函数式风格可能导致性能问题。

### 重构步骤

1. 识别大数据量处理场景
2. 使用生成器（Generator）、Stream 或惰性列表
3. 只计算实际需要的结果

### 示例

```javascript
// 重构前：创建大量中间数组
const result = hugeArray
  .map(x => x * 2)
  .filter(x => x > 100)
  .slice(0, 10);

// 重构后：使用生成器惰性计算
function* processHugeArray(array) {
  let count = 0;
  for (const x of array) {
    const doubled = x * 2;
    if (doubled > 100) {
      yield doubled;
      count++;
      if (count >= 10) break;
    }
  }
}

// 或使用支持惰性的库
const result = Lazy(hugeArray)
  .map(x => x * 2)
  .filter(x => x > 100)
  .take(10)
  .toArray();
```

---

## 模式 9：将回调地狱转换为组合/Monad 链

### 场景
深层嵌套的异步回调或条件分支。

### 重构步骤

1. 将回调函数提取为命名函数
2. 使用 Promise/async-await 或 Monad 链式调用
3. 用 `map`/`flatMap` 替代嵌套

### 示例

```javascript
// 重构前
getUser(id, (err, user) => {
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

// 重构后（async/await）
async function processUserOrders(id) {
  const user = await getUser(id);
  const orders = await getOrders(user.id);
  const result = await processOrders(orders);
  await saveResult(result);
  sendNotification(user, result);
}

// 重构后（函数组合 + Result Monad）
const processUserOrders = pipe(
  getUser,
  chain(user => map(orders => ({ user, orders }), getOrders(user.id))),
  chain(({ orders }) => processOrders(orders)),
  chain(saveResult),
  map(tap(sendNotification))
);
```

---

## 模式 10：引入代数数据类型（ADTs）

### 场景
使用字符串或布尔值表示互斥状态，导致无效状态可表示。

### 重构步骤

1. 识别表示状态或结果的互斥类型
2. 定义和类型（Sum Types）显式建模所有可能状态
3. 使用模式匹配处理各分支

### 示例

```typescript
// 重构前：使用字符串表示状态，允许无效组合
interface Order {
  status: 'pending' | 'paid' | 'shipped' | 'delivered';
  trackingNumber?: string; // 只在 shipped/delivered 时有意义
  paidAt?: Date;           // 只在 paid 后有
}

// 重构后：用 ADT 使无效状态无法表示
type Order =
  | { _tag: 'Pending'; createdAt: Date }
  | { _tag: 'Paid'; createdAt: Date; paidAt: Date }
  | { _tag: 'Shipped'; createdAt: Date; paidAt: Date; trackingNumber: string }
  | { _tag: 'Delivered'; createdAt: Date; paidAt: Date; trackingNumber: string; deliveredAt: Date };

// 模式匹配处理
const getTrackingNumber = (order: Order): Option<string> =>
  order._tag === 'Shipped' || order._tag === 'Delivered'
    ? some(order.trackingNumber)
    : none;
```
