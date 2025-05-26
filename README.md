# **Mini-C Compiler**  
*A Simple Educational Compiler for a C-like Subset*

## **Overview**  
This project is a **Mini-C compiler** that demonstrates the fundamental phases of compilation:  
1. **Lexical Analysis** (tokenization)  
2. **Syntax Analysis** (parsing into an Abstract Syntax Tree)  
3. **Intermediate Code Generation** (Three-Address Code)  

Built using **Python** with **PLY (Lex-Yacc)**, it provides a **web-based interface** (Flask) for interactive compilation.  

---

## **Key Features**  

### **1. Lexical Analysis (Tokenizer)**  
- Recognizes **keywords** (`if`, `else`, `while`, `int`, `return`, `void`)  
- Handles **identifiers**, **numbers**, and **operators** (`+`, `-`, `*`, `/`, `==`, `=`)  
- Supports **arrays** (`arr[10]`) and **function calls**  

### **2. Syntax Analysis (Parser)**  
- Constructs an **Abstract Syntax Tree (AST)**  
- Validates grammar rules for:  
  - **Variable & array declarations**  
  - **Expressions & assignments**  
  - **Control flow (`if`, `else`, `while`)**  
  - **Function definitions & calls**  

### **3. Intermediate Code Generation**  
- Produces **Three-Address Code (TAC)**  
- Supports:  
  - **Temporary variables** (`t0`, `t1`, ...)  
  - **Labels** (`L0`, `L1`, ...) for control flow  
  - **Function calls** and **array access**  

### **4. Web Interface (Flask)**  
- **Input:** Write or paste Mini-C code  
- **Output:**  
  - **Token stream** (lexer output)  
  - **AST** (formatted tree structure)  
  - **Generated TAC** (intermediate code)  
  - **Syntax-highlighted code** (Pygments)  

---

## **Example Input & Output**  

### **Input Code**  
```c
int main() {
    int arr[10];
    arr[0] = 5;
    return arr[0];
}
```

### **Generated Three-Address Code (TAC)**  
```
func main:
var arr
array arr 10
t0 = 0
t1 = 5
arr[t0] = t1
t2 = 0
t3 = arr[t2]
return t3
```

---

## **Installation & Setup**  

### **1. Clone the Repository**  
```bash
git clone https://github.com/Dishank-Kumar/mini-c-compiler.git
cd mini-c-compiler
```

### **2. Install Dependencies**  
```bash
pip install ply pygments flask
```

### **3. Run the Web App**  
```bash
python app.py
```
- Open `http://localhost:5000` in a browser.  

---

## **Supported Syntax**  

### **Variables & Arrays**  
```c
int x;
int arr[5];
```

### **Expressions & Assignments**  
```c
x = 10 + 5 * 2;
arr[0] = x;
```

### **Control Flow**  
```c
if (x == 10) {
    return x;
} else {
    x = 0;
}
```

```c
while (x < 10) {
    x = x + 1;
}
```

### **Functions**  
```c
int add(int a, int b) {
    return a + b;
}
```

---

## **Limitations**  
⚠ **This is an educational project, not a full C compiler.**  
- No **type checking** (e.g., `void x = 5;` is allowed)  
- No **semantic analysis** (e.g., undeclared variables not detected)  
- No **optimizations** (e.g., constant folding, dead code elimination)  
- No **memory management** (e.g., pointers, dynamic allocation)  

---

## **Future Improvements**  
✅ **Symbol table** for semantic analysis  
✅ **Type checking**  
✅ **Optimizations** (e.g., constant propagation)  
✅ **Machine code generation** (via LLVM or x86 ASM)  

---

## **License**  
MIT License – Free for educational and personal use.  

---

## **Contributing**  
Feel free to fork, improve, and submit pull requests!  

🚀 **Happy Compiling!** 🚀
