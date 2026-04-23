# 多语言函数式编程实践指南

本文档提供 JavaScript/TypeScript、Python、Java 等主流语言的函数式编程实践建议。在指导具体语言的代码时，加载并遵循对应章节。

---

## JavaScript / TypeScript

### 不可变性

- 默认使用 `const`，仅在明确需要重新赋值时使用 `let`
- 避免 `var`（作用域提升问题）
- 使用展开运算符创建对象/数组副本：

```typescript
const newObj = { ...oldObj, field: 'new value' };
const newArr = [...oldArr, newItem];
```

- 使用 `Object.freeze` 或 `Readonly<T>` 标记不可变对象（浅冻结）
- 对于深层不可变，使用 `as const`（TS）、`readonly` 修饰符或库（Immutable.js、Immer）

```typescript
// TypeScript readonly
interface Point {
  readonly x: number;
  readonly y: number;
}

// as const
const config = { host: 'localhost', port: 3000 } as const;
```

### 数组操作

优先使用声明式方法替代循环：

```typescript
const result = items
  .filter(item => item.active)
  .map(item => transform(item))
  .reduce((sum, item) => sum + item.value, 0);
```

避免使用可变方法：

| 避免使用 | 替代方案 |
|---------|---------|
| `arr.push(x)` | `[...arr, x]` |
| `arr.pop()` | `arr.slice(0, -1)` |
| `arr.shift()` | `arr.slice(1)` |
| `arr.splice(i, 1)` | `[...arr.slice(0, i), ...arr.slice(i + 1)]` |
| `arr.sort(fn)` | `[...arr].sort(fn)` |
| `arr.reverse()` | `[...arr].reverse()` |

### 对象操作

```typescript
// 添加/更新属性
const updated = { ...obj, newKey: 'value' };

// 删除属性
const { removed, ...rest } = obj;

// 重命名属性
const { oldName: newName, ...others } = obj;
```

### 函数

- 优先使用箭头函数（词法作用域，无 `this` 绑定问题）
- 使用默认参数替代 `||` 回退
- 使用解构使参数意图清晰

```typescript
// 好的实践
const calculateArea = ({ width, height }: Rectangle) => width * height;

// 避免
const calculateArea = (rect) => rect.width * rect.height;
```

### TypeScript 类型工具

- 使用 `Readonly<T>`、`ReadonlyArray<T>` 表达不可变
- 使用 `Partial<T>`、`Required<T>` 进行类型转换
- 使用 `Option<T>` / `Result<T, E>` 替代 `null` / 异常

```typescript
type Option<T> = Some<T> | None;
type Result<T, E> = Ok<T> | Err<E>;
```

### 推荐工具库

- **Ramda**：纯函数工具库，函数优先、数据最后
- **fp-ts**：TypeScript 函数式编程工具箱（ADT、Monad）
- **Immer**：不可变更新的简化写法
- **lodash/fp**：lodash 的函数式变体

---

## Python

### 不可变性

- 优先使用不可变类型：`tuple` 替代 `list`，`frozenset` 替代 `set`
- 使用 `dataclasses` 并设置 `frozen=True`
- 使用 `NamedTuple` 或 `@dataclass(frozen=True)` 定义数据结构

```python
from dataclasses import dataclass
from typing import NamedTuple

# frozen dataclass
@dataclass(frozen=True)
class Point:
    x: float
    y: float

# NamedTuple（自动不可变）
class Point(NamedTuple):
    x: float
    y: float
```

### 列表与字典操作

使用推导式和生成器表达式替代循环：

```python
# map / filter
names = [user.name for user in users if user.active]

# reduce（ functools.reduce ）
from functools import reduce
total = reduce(lambda acc, item: acc + item.price, items, 0)

# 不可变字典更新
new_dict = {**old_dict, "key": "value"}
```

避免使用可变默认参数（Python 经典坑）：

```python
# 错误
def append_item(item, items=[]):
    items.append(item)
    return items

# 正确
from typing import Sequence

def append_item(item: int, items: Sequence[int] = ()) -> tuple[int, ...]:
    return (*items, item)
```

### 函数

- 使用 `functools` 模块：`partial`、`reduce`、`lru_cache`、`wraps`
- 使用 `operator` 模块替代 lambda：`operator.add`、`operator.itemgetter`
- 使用 `itertools` 进行惰性迭代

```python
from functools import partial, reduce
from operator import add, itemgetter

# partial application
multiply_by_2 = partial(operator.mul, 2)

# operator 替代 lambda
users_sorted = sorted(users, key=itemgetter('age'))
```

### 类设计

- 将类设计为不可变数据容器
- 避免在类中维护可变状态
- 方法应返回新实例而非修改自身

```python
from dataclasses import dataclass

@dataclass(frozen=True)
class BankAccount:
    balance: float

    def deposit(self, amount: float) -> "BankAccount":
        return BankAccount(self.balance + amount)
```

### 推荐工具库

- **toolz**：函数式编程工具集（Pythonic 版 Ramda）
- **pyrsistent**：持久化不可变数据结构
- **returns**：Result、Maybe、IO 等 Monad 实现

---

## Java

### 不可变性

- 将类字段声明为 `final`
- 不提供 setter 方法
- 在构造函数中进行防御性拷贝
- 使用不可变集合：`List.of()`、`Set.of()`、`Map.of()`（Java 9+）
- 使用 `Collections.unmodifiableXxx()` 包装可变集合

```java
public final class Point {
    private final double x;
    private final double y;

    public Point(double x, double y) {
        this.x = x;
        this.y = y;
    }

    public Point translate(double dx, double dy) {
        return new Point(x + dx, y + dy); // 返回新实例
    }

    // getters only, no setters
    public double getX() { return x; }
    public double getY() { return y; }
}
```

### Stream API

优先使用 Stream 替代命令式循环：

```java
// 声明式
List<String> activeNames = users.stream()
    .filter(User::isActive)
    .map(User::getName)
    .collect(Collectors.toList());

// 聚合
BigDecimal total = orders.stream()
    .map(Order::getAmount)
    .reduce(BigDecimal.ZERO, BigDecimal::add);
```

### Optional

使用 `Optional<T>` 替代 `null`：

```java
// 避免
String city = user.getAddress().getCity(); // 可能 NPE

// 使用 Optional
String city = Optional.ofNullable(user)
    .map(User::getAddress)
    .map(Address::getCity)
    .orElse("Unknown");
```

### 函数式接口

善用内置函数式接口：

| 接口 | 用途 |
|------|------|
| `Function<T, R>` | T -> R 转换 |
| `Predicate<T>` | T -> boolean 判断 |
| `Consumer<T>` | T -> void 消费 |
| `Supplier<T>` | () -> T 供给 |
| `UnaryOperator<T>` | T -> T 一元操作 |
| `BinaryOperator<T>` | (T, T) -> T 二元操作 |

### 模式匹配（Java 17+）

使用 `switch` 表达式和模式匹配处理 ADT：

```java
sealed interface Shape permits Circle, Rectangle, Triangle { }

record Circle(double radius) implements Shape { }
record Rectangle(double width, double height) implements Shape { }
record Triangle(double base, double height) implements Shape { }

double area(Shape shape) {
    return switch (shape) {
        case Circle c -> Math.PI * c.radius() * c.radius();
        case Rectangle r -> r.width() * r.height();
        case Triangle t -> 0.5 * t.base() * t.height();
    };
}
```

### 推荐工具库

- **Vavr**：Java 函数式编程库（提供 Tuple、Option、Try、Stream、Pattern Matching）
- **Immutables**：不可变对象代码生成器

---

---

## C#

### 不可变性

- `readonly` 字段、init-only 属性（C# 9+ `init` accessor）
- `record` 类型（C# 9+）：值语义，自动支持 `with` 表达式创建副本
- `ImmutableArray<T>`、`ImmutableList<T>`（System.Collections.Immutable）

```csharp
// record（不可变值语义）
public record Point(double X, double Y);

// init-only 属性
public class Config
{
    public string Host { get; init; }
    public int Port { get; init; }
}

// with 表达式
var p2 = p1 with { X = 10 };
```

### 集合操作（LINQ）

优先使用 LINQ 方法替代循环：

```csharp
using System.Linq;

var activeNames = users
    .Where(u => u.IsActive)
    .Select(u => u.Name)
    .ToList();

var total = orders.Sum(o => o.Amount);
```

### 函数

- 函数是一等公民：`Func<T, R>`、`Action<T>`、`Predicate<T>`
- Lambda 表达式：`x => x * 2`
- 模式匹配和 switch 表达式（C# 8+）

```csharp
Func<int, int> double_ = x => x * 2;
var adults = users.Where(u => u.Age >= 18);
```

### 可选值与错误处理

- 可空引用类型（C# 8+ `?`）：`string? name`
- 空合并运算符：`??`、`??=`、`?.`
- 自定义 `Result<T, E>` 或使用 `LanguageExt` 库

```csharp
string city = user?.Address?.City ?? "Unknown";
```

### 推荐工具库

- **LanguageExt**：C# 函数式编程库（Option、Either、Reader、Writer、State Monad）
- **System.Collections.Immutable**：不可变集合

---

## Go

### 不可变性

Go 没有 `const` 对象（只有标量常量），不可变性主要靠**值传递**和**值语义**：
- `struct` 默认按值传递，天然适合不可变风格
- 切片（slice）和 map 是引用类型，需要显式拷贝
- 字符串本身不可变

```go
type Point struct{ X, Y float64 }

func Translate(p Point, dx, dy float64) Point {
    return Point{p.X + dx, p.Y + dy} // 返回新实例
}
```

### 集合操作

Go 标准库没有 `map`/`filter`/`reduce`，需要手写泛型工具函数（Go 1.18+）：

```go
func Filter[T any](items []T, pred func(T) bool) []T {
    var result []T
    for _, v := range items {
        if pred(v) {
            result = append(result, v)
        }
    }
    return result
}

names := Filter(users, func(u User) bool { return u.Active })
```

### 函数

- 函数是一等公民，支持闭包
- Go 1.18+ 泛型支持泛型高阶函数
- 不支持默认参数和函数重载

```go
func multiplier(factor int) func(int) int {
    return func(x int) int { return x * factor }
}
```

### 可选值与错误处理

Go 的惯用错误处理模式就是 FP 中 `Result<T, error>` 的朴素实现：

```go
func findUser(id string) (*User, error) {
    user, ok := db[id]
    if !ok {
        return nil, errors.New("user not found")
    }
    return user, nil
}

user, err := findUser("123")
if err != nil {
    // handle error
}
```

### 推荐工具库

- Go 生态几乎没有主流 FP 库，主要靠语言本身的值语义和函数支持
- **samber/mo**：Go 的 Option / Result / Either 实现

---

## C++

### 不可变性

- `const` 修饰符（非严格不可变，可通过 `mutable` 成员绕过）
- `constexpr`：编译期常量
- 值语义 + 拷贝构造函数创建新实例
- 借助库实现严格不可变

```cpp
const std::vector<int> nums = {1, 2, 3}; // 不能修改 nums
```

### 集合操作

C++ 标准库算法（STL）提供声明式操作，C++20 Ranges 更加 FP 友好：

```cpp
// C++17 及之前
std::vector<int> doubled;
std::transform(nums.begin(), nums.end(), std::back_inserter(doubled),
               [](int x) { return x * 2; });

// C++20 Ranges（推荐）
auto doubled = nums | std::views::transform([](int x) { return x * 2; });
auto adults = users | std::views::filter([](const User& u) { return u.age >= 18; });
```

### 函数

- Lambda 表达式：`[capture](params){ body }`
- `std::function`、`std::bind`、函数对象
- 泛型 Lambda（C++14 `auto` 参数）

```cpp
auto add = [](int a, int b) { return a + b; };
std::function<int(int)> makeAdder(int x) {
    return [x](int y) { return x + y; };
}
```

### 可选值与错误处理

- `std::optional<T>`（C++17）
- `std::expected<T, E>`（C++23）
- `std::variant<T, E>`（C++17）模拟 Either

```cpp
#include <optional>

std::optional<User> findUser(const std::string& id) {
    auto it = db.find(id);
    if (it != db.end()) return it->second;
    return std::nullopt;
}

auto user = findUser("123");
if (user.has_value()) { /* ... */ }
```

### 推荐工具库

- **range-v3**：Eric Niebler 的 Ranges 库（C++20 Ranges 的前身，功能更丰富）
- **tl::optional / tl::expected**：低版本编译器的 polyfill

---

## Rust

### 不可变性

Rust 的**默认不可变**是最大亮点：
- `let` 默认不可变，`let mut` 显式声明可变
- 所有权系统强制数据不共享可变状态

```rust
let x = 5;        // 不可变
let mut y = 5;    // 显式可变

let r1 = &x;      // 不可变借用（可同时存在多个）
let r2 = &x;
```

### 集合操作

Rust 的迭代器是**惰性**的，标准库直接支持 FP 风格：

```rust
let names: Vec<String> = users
    .iter()
    .filter(|u| u.is_active)
    .map(|u| u.name.clone())
    .collect();

let total: i32 = orders.iter().map(|o| o.amount).sum();
```

### 函数

- 闭包 `|x| x + 1`
- 高阶函数、函数指针 `fn`
- Trait bounds 实现泛型高阶函数

```rust
fn apply<T, F>(value: T, f: F) -> T
where
    F: Fn(T) -> T,
{
    f(value)
}

let result = apply(5, |x| x * 2);
```

### 可选值与错误处理

`Option<T>` 和 `Result<T, E>` 是标准库核心类型，模式匹配是惯用写法：

```rust
fn find_user(id: &str) -> Option<&User> {
    db.get(id)
}

let street = find_user("123")
    .and_then(|u| u.address.as_ref())
    .map(|a| a.street.as_str())
    .unwrap_or("Unknown");

// Result 的错误传播
fn parse_config(path: &str) -> Result<Config, Error> {
    let content = std::fs::read_to_string(path)?; // ? 运算符
    let config: Config = serde_json::from_str(&content)?;
    Ok(config)
}
```

### 推荐工具库

- **itertools**：扩展迭代器，提供更多组合子
- **rayon**：数据并行迭代器（`par_iter()`），无副作用代码自动并行化
- **frunk**：HList、LabelledGeneric 等高级 FP 工具

---

## Kotlin

### 不可变性

- `val`（只读变量）vs `var`（可变变量）
- `data class` 自动生成 `copy()` 方法
- 不可变集合：`listOf()`、`setOf()`、`mapOf()`

```kotlin
data class User(val name: String, val age: Int)

val user = User("Alice", 30)
val updated = user.copy(age = 31) // 新实例
```

### 集合操作

Kotlin 标准库直接提供声明式操作，无需额外库：

```kotlin
val activeNames = users
    .filter { it.isActive }
    .map { it.name }

val total = orders.sumOf { it.amount }
```

### 函数

- 函数是一等公民
- 高阶函数、扩展函数、尾递归 `tailrec`
- Lambda 语法简洁：`{ it.name }`

```kotlin
// 扩展函数
fun String.addExclamation() = this + "!"

// 尾递归
 tailrec fun factorial(n: Int, acc: Int = 1): Int =
    if (n <= 1) acc else factorial(n - 1, n * acc)
```

### 可选值与错误处理

- 可空类型 `T?` 编译期检查
- 安全调用 `?.`、Elvis `?:`
- `let` / `run` / `apply` / `also` 作用域函数
- 标准库 `Result<T>`

```kotlin
val city = user?.address?.city ?: "Unknown"

val result = runCatching { riskyOperation() }
    .map { it * 2 }
    .getOrDefault(0)
```

### 推荐工具库

- **Arrow.kt**：Kotlin 函数式编程库（Option、Either、IO、Optics）
- Kotlin 标准库已内置大量 FP 工具

---

## Swift

### 不可变性

- `let`（常量）vs `var`（变量）
- `struct` 是值类型，默认 copy-on-write，天然适合不可变风格
- `class` 是引用类型，需要刻意避免可变状态

```swift
struct Point {
    let x: Double
    let y: Double
    
    func translate(dx: Double, dy: Double) -> Point {
        return Point(x: x + dx, y: y + dy)
    }
}

let p = Point(x: 1, y: 2)
let p2 = p.translate(dx: 3, dy: 4) // p 未被修改
```

### 集合操作

Swift 标准库集合类型直接支持高阶函数：

```swift
let activeNames = users
    .filter { $0.isActive }
    .map { $0.name }

let total = orders.reduce(0) { $0 + $1.amount }
```

### 函数

- 函数是一等公民
- 闭包简写：`{ $0 * 2 }`
- 尾随闭包（Trailing Closure）

```swift
let doubled = numbers.map { $0 * 2 }

func apply<T>(_ value: T, _ transform: (T) -> T) -> T {
    return transform(value)
}
```

### 可选值与错误处理

- `Optional<T>`（`T?`）是标准类型
- 可选链 `?.`、空合运算符 `??`
- `guard let`、`if let` 绑定
- `Result<T, Error>` 类型

```swift
let city = user?.address?.city ?? "Unknown"

let result = Result { try parseConfig(path: "config.json") }
    .map { $0.port }
    .getOrElse(8080)
```

### 推荐工具库

- Swift 标准库已提供完善的 FP 支持
- **Bow**：Swift 函数式编程库（Option、Either、Monad、Optics）

---

## PHP

### 不可变性

PHP 没有原生不可变对象，主要靠编码约定：
- `final class` + 私有属性 + 无 setter + 构造函数赋值
- `readonly` 属性（PHP 8.1+）

```php
// PHP 8.1+ readonly
final class Point
{
    public function __construct(
        public readonly float $x,
        public readonly float $y
    ) {}
}
```

### 集合操作

传统数组函数 + PHP 8.4 新增 `array_find`：

```php
$names = array_map(
    fn($u) => $u->name,
    array_filter($users, fn($u) => $u->active)
);

// PHP 8.4+
$found = array_find($users, fn($u) => $u->id === 123);
```

### 函数

- 匿名函数（Closure）、箭头函数 `fn() =>`（PHP 7.4+）
- 函数是一等公民
- 不支持泛型

```php
$double = fn(int $x): int => $x * 2;
$adults = array_filter($users, fn($u) => $u->age >= 18);
```

### 可选值与错误处理

- 没有 Option 类型，用 `?Type`（PHP 8+）或 null 检查
- 可选链 `?->`（PHP 8.0+）
- 异常控制流 `try/catch/throw`

```php
function findUser(string $id): ?User {
    return $db[$id] ?? null;
}

$name = findUser("123")?->name ?? "Unknown";
```

### 推荐工具库

- PHP 生态中成熟 FP 库较少
- **lstrojny/functional-php**：常用高阶函数集合

---

## 通用对比速查表

| 概念 | JS/TS | Python | Java | C# | Go | Rust | Kotlin |
|------|-------|--------|------|----|----|------|--------|
| 常量声明 | `const` | 约定大写（无原生常量） | `final` | `readonly` / `init` | `const`（仅标量） | `let`（默认不可变） | `val` |
| 不可变列表 | `[...arr]` / `ReadonlyArray` | `tuple` | `List.of()` / `Collections.unmodifiableList` | `ImmutableArray` | 切片拷贝（无原生） | `Vec`（默认不可变借用） | `listOf()` |
| 不可变对象 | `{...obj}` / `Object.freeze` | `dataclass(frozen=True)` | 全 `final` 字段 + `record` | `record` / `with` | `struct`（值语义） | `struct`（默认不可变字段） | `data class` + `copy()` |
| 映射 | `arr.map(fn)` | `[fn(x) for x in arr]` | `stream.map(fn)` | `Select(fn)` | 手写 / 泛型 | `iter().map(fn)` | `map { }` |
| 筛选 | `arr.filter(fn)` | `[x for x in arr if cond]` | `stream.filter(fn)` | `Where(fn)` | 手写 / 泛型 | `iter().filter(fn)` | `filter { }` |
| 归约 | `arr.reduce(fn, init)` | `functools.reduce(fn, arr, init)` | `stream.reduce(fn, init)` | `Aggregate(fn, init)` | 手写 / 泛型 | `iter().fold(init, fn)` | `fold { }` / `reduce { }` |
| 可选值 | `?.` / `??` / 自定义 Option | `Optional[T]` / 自定义 | `Optional<T>` | `T?` / `??` / `?.` | `(T, error)` 多返回值 | `Option<T>` | `T?` / `?.` / `?:` |
| 错误处理 | `Result<T,E>` / `try/catch` | `Result` / `try/except` | `Optional` / `try/catch` / Vavr `Try` | `Result<T>` / `try/catch` | `(T, error)` 多返回值 | `Result<T, E>` | `Result<T>` / `runCatching` |
| 函数组合 | `pipe` / `compose` | `toolz.compose` / `toolz.pipe` | `Function.andThen` / `Function.compose` | 方法链 / `Compose` | 手写 | 方法链 / 闭包组合 | 方法链 / `andThen` |
| 惰性求值 | Generator / 惰性库 | Generator / `itertools` | `Stream`（已惰性） | `IEnumerable` / `yield` | 手写 Generator | `Iterator`（已惰性） | `Sequence`（已惰性） |

---

## 语言无关原则

无论使用哪种语言，以下原则始终适用：

1. **偏好表达式而非语句** — 使代码更简洁、可组合
2. **偏好不可变数据** — 减少认知负担和 bug 来源
3. **拆分小函数** — 每个函数只做一件事，易于测试和复用
4. **显式优于隐式** — 依赖应在类型签名和参数中可见
5. **让非法状态不可表示** — 利用类型系统排除无效组合
6. **副作用隔离** — 将纯逻辑与不纯操作严格分离
