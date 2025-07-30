# 🚀 Hướng dẫn Upload Cognify SDK lên PyPI

## 📋 **Yêu cầu trước khi upload**

### 1. **Tài khoản PyPI**
- Tạo tài khoản tại: https://pypi.org/account/register/
- Tạo tài khoản TestPyPI tại: https://test.pypi.org/account/register/
- Xác thực email cho cả hai tài khoản

### 2. **API Tokens**
- Tạo API token tại: https://pypi.org/manage/account/token/
- Tạo API token cho TestPyPI tại: https://test.pypi.org/manage/account/token/
- Lưu tokens an toàn (chỉ hiển thị 1 lần)

---

## 🛠️ **Bước 1: Cài đặt build tools**

```bash
# Cài đặt build và upload tools
pip install --upgrade pip
pip install build twine

# Hoặc cài đặt với hatch (recommended)
pip install hatch
```

---

## 🔧 **Bước 2: Chuẩn bị project**

### **Kiểm tra cấu trúc project**
```bash
# Đảm bảo cấu trúc đúng
cognify-py-sdk/
├── cognify_sdk/           # Main package
│   ├── __init__.py
│   └── ...
├── pyproject.toml         # Build configuration
├── README.md              # Package description
├── LICENSE               # License file (cần tạo)
└── CHANGELOG.md          # Version history (optional)
```

### **Tạo LICENSE file**
```bash
# Tạo MIT License
cat > LICENSE << 'EOF'
MIT License

Copyright (c) 2025 Cognify Team

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
EOF
```

---

## 📦 **Bước 3: Build package**

### **Clean previous builds**
```bash
# Xóa build cũ
rm -rf dist/ build/ *.egg-info/
```

### **Build package**
```bash
# Build với python -m build
python -m build

# Hoặc với hatch
hatch build
```

### **Kiểm tra build output**
```bash
# Kiểm tra files được tạo
ls -la dist/
# Sẽ có:
# cognify_sdk-0.1.0-py3-none-any.whl
# cognify_sdk-0.1.0.tar.gz
```

---

## 🧪 **Bước 4: Test upload lên TestPyPI**

### **Upload lên TestPyPI**
```bash
# Upload lên TestPyPI để test
twine upload --repository testpypi dist/*

# Nhập credentials khi được hỏi:
# Username: __token__
# Password: [your-testpypi-api-token]
```

### **Test install từ TestPyPI**
```bash
# Tạo virtual environment mới để test
python -m venv test_env
source test_env/bin/activate  # Linux/Mac
# test_env\Scripts\activate   # Windows

# Install từ TestPyPI
pip install --index-url https://test.pypi.org/simple/ --extra-index-url https://pypi.org/simple/ cognify-sdk

# Test import
python -c "from cognify_sdk import CognifyClient; print('✅ Import successful')"
```

---

## 🚀 **Bước 5: Upload lên PyPI chính thức**

### **Upload production**
```bash
# Upload lên PyPI chính thức
twine upload dist/*

# Nhập credentials:
# Username: __token__
# Password: [your-pypi-api-token]
```

### **Verify upload**
```bash
# Kiểm tra package trên PyPI
# https://pypi.org/project/cognify-sdk/

# Test install từ PyPI
pip install cognify-sdk
```

---

## 🔐 **Bước 6: Cấu hình credentials (Optional)**

### **Tạo ~/.pypirc file**
```bash
cat > ~/.pypirc << 'EOF'
[distutils]
index-servers =
    pypi
    testpypi

[pypi]
username = __token__
password = [your-pypi-api-token]

[testpypi]
repository = https://test.pypi.org/legacy/
username = __token__
password = [your-testpypi-api-token]
EOF

# Bảo mật file
chmod 600 ~/.pypirc
```

---

## 📋 **Checklist trước khi upload**

### ✅ **Pre-upload checklist**
- [ ] Tài khoản PyPI và TestPyPI đã tạo
- [ ] API tokens đã tạo và lưu an toàn
- [ ] `pyproject.toml` đã cấu hình đúng
- [ ] `README.md` đã viết đầy đủ
- [ ] `LICENSE` file đã tạo
- [ ] Version number đã update
- [ ] Dependencies đã kiểm tra
- [ ] Package đã test local
- [ ] Build tools đã cài đặt

### ✅ **Upload checklist**
- [ ] Clean previous builds
- [ ] Build package thành công
- [ ] Upload lên TestPyPI thành công
- [ ] Test install từ TestPyPI thành công
- [ ] Upload lên PyPI thành công
- [ ] Verify package trên PyPI
- [ ] Test install từ PyPI thành công

---

## 🔄 **Bước 7: Update versions (Future releases)**

### **Semantic Versioning**
```
0.1.0 -> 0.1.1 (patch: bug fixes)
0.1.1 -> 0.2.0 (minor: new features)
0.2.0 -> 1.0.0 (major: breaking changes)
```

### **Update process**
1. Update version trong `pyproject.toml`
2. Update `CHANGELOG.md`
3. Commit changes
4. Create git tag: `git tag v0.1.1`
5. Build và upload new version

---

## 🚨 **Lưu ý quan trọng**

### **Security**
- ⚠️ **KHÔNG** commit API tokens vào git
- ⚠️ **KHÔNG** share API tokens
- ✅ Sử dụng environment variables hoặc ~/.pypirc

### **Package naming**
- ⚠️ Package name `cognify-sdk` phải unique trên PyPI
- ✅ Kiểm tra tên đã tồn tại: https://pypi.org/project/cognify-sdk/
- ✅ Nếu tên đã tồn tại, đổi thành `cognify-python-sdk` hoặc tương tự

### **Dependencies**
- ✅ Chỉ include dependencies thực sự cần thiết
- ✅ Specify version ranges hợp lý
- ✅ Test với Python versions khác nhau

---

## 📞 **Hỗ trợ**

Nếu gặp vấn đề:
1. Kiểm tra PyPI status: https://status.python.org/
2. Đọc PyPI docs: https://packaging.python.org/
3. Kiểm tra logs chi tiết từ twine
4. Test với TestPyPI trước

**Good luck! 🚀**
