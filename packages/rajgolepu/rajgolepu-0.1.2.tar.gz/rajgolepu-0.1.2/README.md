# rajgolepu

```
     ___       _       _                 
    | _ \_ _ _(_)___ __| |_  ___ _ _ ___  
    |  _/ '_| '_/ -_|_-< ' \/ -_) '_/ -_) 
    |_| |_| |_| \___/__/_||_\___|_| \___| 
```

📦 A personal Python package and CLI tool by **Raj Golepu**, showcasing portfolio links and handy utilities.

## 🚀 Usage

### 🔹 In Python

```python
import rajgolepu

rajgolepu.info()
rajgolepu.help()

print(rajgolepu.format_title_case("hello world"))
print(rajgolepu.reverse_string("python"))
print("Vowels:", rajgolepu.count_vowels("encyclopedia"))

@rajgolepu.timer
def test(): sum(range(10**6))
test()
```

### 🔹 From the CLI

```bash
rajgolepu --info
rajgolepu --format "hello world"
rajgolepu --reverse "python"
rajgolepu --vowels "encyclopedia"
rajgolepu --time
rajgolepu --help
```

## 🧰 Features

- Portfolio CLI
- Title Case formatter
- String reverser
- Vowel counter
- Timer decorator
- ASCII banner printer
- Help menu

## 📇 Author

Raj Golepu  
🔗 [GitHub](https://github.com/rajgolepu)  
💼 [LinkedIn](https://linkedin.com/in/rajgolepu)
