#!/bin/bash
# =============================================================================
# Weaver Gemma 4 Setup Script - إعداد Gemma 4 للمشروع
# =============================================================================

set -e

echo "🔮 Weaver Gemma 4 Setup"
echo "======================="
echo ""

# ألوان
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# التحقق من النظام
check() {
    if command -v $1 &> /dev/null; then
        echo -e "${GREEN}✓${NC} $1 مثبت"
        return 0
    else
        echo -e "${YELLOW}✗${NC} $1 غير مثبت"
        return 1
    fi
}

# التثبيت
install() {
    echo -e "${GREEN}→${NC} جاري التثبيت: $1"
    $2
}

# =============================================================================
# 1. التحقق من Ollama
# =============================================================================
echo "1. فحص Ollama..."
echo "----------------"

if check ollama; then
    echo -e "\n${GREEN}✓ Ollama مثبت مسبقاً${NC}"
    ollama --version
else
    echo ""
    echo "Ollama غير مثبت. للتثبيت:"
    echo "  Linux/Mac: curl -fsSL https://ollama.com/install.sh | sh"
    echo "  Windows: تحميل من https://ollama.com/download"
    echo ""
    read -p "هل تريد المتابعة بدون Ollama? (y/n) " -n 1 -r
    echo ""
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

# =============================================================================
# 2. اختيار النموذج
# =============================================================================
echo ""
echo "2. اختيار نموذج Gemma 4..."
echo "--------------------------"
echo ""
echo "  1) gemma4:12b-it-qat  - 16GB RAM (موصى به للأحلام المعقدة)"
echo "  2) gemma4:12b         - 24GB RAM (نسخة كاملة)"
echo "  3) gemma4:2b-it-qat   - 4GB RAM (للأجهزة المحدودة)"
echo "  4) gemma4:2b          - 6GB RAM (نسخة كاملة خفيفة)"
echo ""

read -p "اختر النموذج (1-4) [الافتراضي: 1]: " choice
choice=${choice:-1}

case $choice in
    1) MODEL="gemma4:12b-it-qat" ;;
    2) MODEL="gemma4:12b" ;;
    3) MODEL="gemma4:2b-it-qat" ;;
    4) MODEL="gemma4:2b" ;;
    *) MODEL="gemma4:12b-it-qat" ;;
esac

echo -e "\n${GREEN}✓${NC} النموذج المختار: $MODEL"

# =============================================================================
# 3. تحميل النموذج
# =============================================================================
echo ""
echo "3. تحميل نموذج Gemma 4..."
echo "-------------------------"
echo ""
echo -e "${YELLOW}هذا قد يستغرق بعض الوقت حسب سرعة الإنترنت...${NC}"
echo ""

read -p "هل تريد تحميل النموذج الآن? (y/n) " -n 1 -r
echo ""

if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo "جاري التحميل..."
    ollama pull $MODEL
    echo -e "${GREEN}✓${NC} تم تحميل النموذج بنجاح!"
else
    echo "للتحميل لاحقاً: ollama pull $MODEL"
fi

# =============================================================================
# 4. إنشاء ملف .env
# =============================================================================
echo ""
echo "4. إعداد ملف البيئة..."
echo "----------------------"

ENV_FILE=".env"
if [ -f "$ENV_FILE" ]; then
    echo -e "${YELLOW}ملف .env موجود مسبقاً${NC}"
    read -p "هل تريد تحديثه? (y/n) " -n 1 -r
    echo ""
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo "تم الاحتفاظ بالملف الحالي"
    else
        cat >> "$ENV_FILE" << EOF

# Ollama / Gemma 4
OLLAMA_BASE_URL=http://localhost:11434
GEMMA4_MODEL=$MODEL
EOF
        echo -e "${GREEN}✓${NC} تم تحديث $ENV_FILE"
    fi
else
    cat > "$ENV_FILE" << EOF
# Ollama / Gemma 4
OLLAMA_BASE_URL=http://localhost:11434
GEMMA4_MODEL=$MODEL
EOF
    echo -e "${GREEN}✓${NC} تم إنشاء $ENV_FILE"
fi

# =============================================================================
# 5. التحقق النهائي
# =============================================================================
echo ""
echo "5. التحقق من الإعداد..."
echo "----------------------"

echo "جاري تشغيل Ollama..."
if ! pgrep -x "ollama" > /dev/null; then
    echo "بدء Ollama في الخلفية..."
    ollama serve > /dev/null 2>&1 &
    sleep 3
fi

echo "فحص الاتصال..."
curl -s http://localhost:11434/api/tags > /dev/null 2>&1
if [ $? -eq 0 ]; then
    echo -e "${GREEN}✓${NC} Ollama متصل بنجاح!"
    
    echo ""
    echo "النماذج المتاحة:"
    ollama list | tail -n +2
else
    echo -e "${YELLOW}⚠${NC} Ollama غير متصل. تأكد من تشغيله:"
    echo "   ollama serve"
fi

# =============================================================================
# ملخص
# =============================================================================
echo ""
echo "======================="
echo -e "${GREEN}✓ تم الإعداد بنجاح!${NC}"
echo "======================="
echo ""
echo "للبدء:"
echo "  1. تأكد من تشغيل Ollama: ollama serve"
echo "  2. اختر النموذج:        export GEMMA4_MODEL=$MODEL"
echo "  3. جرب التطبيق:        python ollama_gemma4.py --dream 'حلمك هنا'"
echo ""
echo "للتشغيل مع التطبيق:"
echo "  python -m uvicorn app.main:app --reload --port 8000"
echo ""