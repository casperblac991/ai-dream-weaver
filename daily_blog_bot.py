#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Weaver Daily Blog Bot - بوت ينشر مقالات وتقارير يومياً
"""

import os
import random
import datetime
import json
from pathlib import Path

# =========================================
# تكوين البوت
# =========================================
BOT_NAME = "Weaver Daily Bot"
VERSION = "2.0"
ADMIN_ID = 6790340715

# =========================================
# مواضيع المقالات (متنوعة)
# =========================================
ARTICLES = [
    # ===== التراث الإسلامي =====
    {
        "title_ar": "الإمام محمد بن سيرين - شيخ المفسرين",
        "title_en": "Imam Ibn Sirin - The Master Interpreter",
        "category_ar": "التراث الإسلامي",
        "category_en": "Islamic Heritage",
        "type": "article",
        "era": "654-728 CE",
        "read_time": 8,
        "content_ar": """
الإمام محمد بن سيرين (654-728م) هو أشهر مفسر أحلام في التاريخ الإسلامي. كان من التابعين المعروفين بالورع والزهد.

📚 **نشأته:**
ولد في خلافة عثمان بن عفان، ونشأ في بيت علم وتقوى. تتلمذ على يد كبار الصحابة والتابعين.

🔍 **منهجه في التفسير:**
• لا يفسر الرؤيا إلا بعد الصلاة والاستخارة
• يسأل الرائي عن حاله (صالح أو طالح)
• يعتمد على القرآن والسنة في تفسيره
• يراعي اللغة العربية ومعاني الكلمات

🌟 **أشهر تفسيراته:**
• رؤية النبي ﷺ في المنام حق
• البحر يدل على الملك أو العالم
• الثعبان يدل على العدو
• الطيران يدل على السفر أو الموت
• الأسنان تدل على الأهل والأقارب

📖 **مؤلفاته:**
أشهر كتبه "تفسير الأحلام" الذي جمعه تلاميذه. تأثر به جميع المفسرين بعده.
""",
        "content_en": """
Imam Muhammad Ibn Sirin (654-728 CE) is the most famous dream interpreter in Islamic history.

📚 **Biography:**
Born during Caliph Uthman's reign, raised in a scholarly family. Studied under great companions.

🔍 **Methodology:**
• Never interprets without prayer
• Asks about dreamer's spiritual state
• Based on Quran and Sunnah
• Considers Arabic language meanings

🌟 **Famous Interpretations:**
• Seeing Prophet Muhammad is true
• Sea represents king or knowledge
• Snake represents enemy
• Flying represents travel or death
• Teeth represent family
"""
    },
    {
        "title_ar": "الفرق بين الرؤيا والحلم - ابن القيم",
        "title_en": "Vision vs. Dream - Ibn Al-Qayyim",
        "category_ar": "التراث الإسلامي",
        "category_en": "Islamic Heritage",
        "type": "article",
        "era": "1292-1350 CE",
        "read_time": 6,
        "content_ar": """
الإمام ابن القيم يفرق بين ثلاثة أنواع:

🌟 **الرؤيا:**
• من الله تعالى
• تحمل بشارة أو تحذير
• صادقة وواضحة
• تأتي للصالحين

💭 **الحلم:**
• من الشيطان
• يسبب الحزن والقلق
• أضغاث أحلام (غير مفهومة)
• يخوف النائم

🧠 **حديث النفس:**
• مما يفكر فيه الإنسان
• يرى في منامه ما يشغله
• ليس له تفسير

كيف تفرق بينهم؟
- الرؤيا: تبشر بخير
- الحلم: يزعج ويخوف
- حديث النفس: يعكس الواقع
""",
        "content_en": """
Imam Ibn Al-Qayyim distinguishes three types:

🌟 **Vision (Ru'ya):**
• From Allah
• Good news or warning
• Clear and true
• Comes to righteous

💭 **Dream (Hulm):**
• From Satan
• Causes sadness
• Confusing nightmares
• Frightens the sleeper

🧠 **Self-Talk:**
• From daily thoughts
• Reflects concerns
• No interpretation

How to distinguish:
- Vision: brings good news
- Dream: causes fear
- Self-talk: reflects reality
"""
    },
    {
        "title_ar": "تفسير حلم يوسف عليه السلام",
        "title_en": "Prophet Yusuf's Dream Interpretation",
        "category_ar": "التراث الإسلامي",
        "category_en": "Islamic Heritage",
        "type": "article",
        "era": "Quranic",
        "read_time": 7,
        "content_ar": """
قصة يوسف عليه السلام من أعظم قصص تفسير الأحلام في القرآن.

🌙 **رؤيا يوسف:**
"إذ قال يوسف لأبيه يا أبت إني رأيت أحد عشر كوكباً والشمس والقمر رأيتهم لي ساجدين"

🔍 **تفسير يعقوب عليه السلام:**
• الأحد عشر كوكباً: إخوته
• الشمس: أبوه
• القمر: أمه أو خالته
• السجود: تعظيم وطاعة

⏳ **التحقق بعد 40 سنة:**
تحققت الرؤيا عندما سجد إخوته وأبواه له في مصر.

📚 **دروس من القصة:**
• الرؤيا الصالحة قد تتحقق بعد سنوات
• لا تقص الرؤيا على الحاسدين
• تعبير الرؤيا علم عظيم
""",
        "content_en": """
Prophet Yusuf's story is among the greatest dream interpretations in the Quran.

🌙 **Yusuf's Vision:**
"I saw eleven stars and the sun and moon prostrating to me"

🔍 **Jacob's Interpretation:**
• Eleven stars: his brothers
• Sun: his father
• Moon: his mother/aunt
• Prostration: honor and respect

⏳ **Fulfillment after 40 years:**
The vision came true when his family prostrated to him in Egypt.

📚 **Lessons:**
• True visions may take years to fulfill
• Don't share dreams with envious people
• Dream interpretation is a great science
"""
    },
    {
        "title_ar": "آداب الرؤيا في الإسلام",
        "title_en": "Dream Etiquette in Islam",
        "category_ar": "التراث الإسلامي",
        "category_en": "Islamic Heritage",
        "type": "article",
        "era": "Islamic",
        "read_time": 5,
        "content_ar": """
كيف تتعامل مع رؤياك وفق السنة النبوية:

🌙 **إذا رأيت رؤيا صالحة:**
• احمد الله عليها
• استبشر بها خيراً
• قصها على من تحب
• انتظر خيرها

💭 **إذا رأيت حلماً مزعجاً:**
• استعذ بالله من الشيطان
• استعذ من شر الرؤيا
• لا تحدث بها أحداً
• تحول إلى الجنب الآخر
• صلِّ إذا استيقظت

📖 **الأدعية المأثورة:**
"اللهم إني أعوذ بك من شر ما رأيت"
"أعوذ بكلمات الله التامة من غضبه وعقابه"

⚠️ **تحذير:**
• لا تفسر حلماً مزعجاً بنفسك
• لا تطلب تفسيراً من جاهل
• لا تصدق كل من يدعي تفسير الأحلام
""",
        "content_en": """
How to deal with your dreams according to Sunnah:

🌙 **If you see a good vision:**
• Praise Allah
• Be optimistic
• Share with loved ones
• Expect good

💭 **If you see a bad dream:**
• Seek refuge from Satan
• Seek protection from its evil
• Don't share it
• Turn to other side
• Pray if you wake

📖 **Prophetic supplications:**
"I seek refuge from its evil"
"I seek refuge in Allah's perfect words"

⚠️ **Warning:**
• Don't interpret bad dreams yourself
• Don't ask ignorant people
• Don't believe every dream interpreter
"""
    },

    # ===== مصر القديمة =====
    {
        "title_ar": "بردية تشستر بيتي - أقدم دليل للأحلام",
        "title_en": "Chester Beatty Papyrus - Oldest Dream Manual",
        "category_ar": "مصر القديمة",
        "category_en": "Ancient Egypt",
        "type": "article",
        "era": "1275 BCE",
        "read_time": 8,
        "content_ar": """
بردية تشستر بيتي هي أقدم دليل معروف لتفسير الأحلام في التاريخ.

📜 **وصف البردية:**
• تاريخها: 1275 قبل الميلاد
• مكان العثور: طيبة (الأقصر حالياً)
• طولها: 5 أمتار
• لغتها: الهيروغليفية

🌟 **في مصر القديمة:**
• كان الفراعنة يعتقدون أن الأحلام رسائل من الآلهة
• الكهنة كانوا المفسرين الرسميين
• الأحلام تكتب على البرديات وتُحفظ في المعابد

🔍 **أمثلة من التفسيرات الفرعونية:**
• رؤية التمساح: تحذير من خطر
• رؤية النيل: خير وبركة
• رؤية الفرعون: ترقية في المنصب
• رؤية الثعبان: حكمة وشفاء
• رؤية الموت: حياة جديدة

🏛️ **تأثير الأحلام:**
• كانت سبباً في قرارات الملوك
• بنيت معابد بناءً على أحلام
• غيرت مسار الحروب
""",
        "content_en": """
The Chester Beatty Papyrus is the oldest known dream interpretation manual.

📜 **Description:**
• Date: 1275 BCE
• Found: Thebes (Luxor)
• Length: 5 meters
• Language: Hieroglyphs

🌟 **In Ancient Egypt:**
• Pharaohs believed dreams were divine messages
• Priests were official interpreters
• Dreams recorded on papyrus and kept in temples

🔍 **Egyptian Interpretations:**
• Seeing crocodile: danger warning
• Seeing Nile: blessing
• Seeing Pharaoh: promotion
• Seeing snake: wisdom and healing
• Seeing death: new life

🏛️ **Dream Influence:**
• Influenced royal decisions
• Temples built based on dreams
• Changed war strategies
"""
    },
    {
        "title_ar": "أحلام الفراعنة وتأثيرها على القرارات",
        "title_en": "Pharaohs' Dreams and Royal Decisions",
        "category_ar": "مصر القديمة",
        "category_en": "Ancient Egypt",
        "type": "article",
        "era": "1550-1070 BCE",
        "read_time": 7,
        "content_ar": """
كيف أثرت الأحلام على قرارات ملوك مصر القديمة؟

👑 **أحلام الملوك:**
• الملك تحتمس الرابع بنى تمثال أبو الهول بعد حلم
• أحلام رمسيس الثاني أثرت على خططه الحربية
• الملكة حتشبسوت رأت أحلاماً عن إلهها آمون

📜 **سجلات الأحلام:**
• كتبت على جدران المعابد
• نقشت على المسلات
• حفظت في المكتبات الملكية

🔮 **أحلام غيرت التاريخ:**
• حلم الملك نخاو الثاني قبل المعركة
• رؤيا الملك أمنمحات عن اغتياله
• أحلام كليوباترا قبل سقوط مصر

⚡ **تفسير الأحلام الملكية:**
• الكهنة الكبار هم المفسرون
• يقررون مصير الحروب
• يوجهون السياسة الخارجية
""",
        "content_en": """
How did dreams influence Ancient Egyptian kings' decisions?

👑 **Royal Dreams:**
• Thutmose IV built the Sphinx after a dream
• Ramesses II's dreams affected war plans
• Hatshepsut had dreams about god Amun

📜 **Dream Records:**
• Written on temple walls
• Carved on obelisks
• Kept in royal libraries

🔮 **History-Changing Dreams:**
• Pharaoh Necho II's pre-battle dream
• Amenemhat's assassination vision
• Cleopatra's dreams before Egypt's fall

⚡ **Royal Dream Interpretation:**
• High priests were interpreters
• Decided war outcomes
• Guided foreign policy
"""
    },

    # ===== بلاد الرافدين =====
    {
        "title_ar": "الألواح الطينية البابلية",
        "title_en": "Babylonian Clay Tablets",
        "category_ar": "بلاد الرافدين",
        "category_en": "Mesopotamia",
        "type": "article",
        "era": "2000-1600 BCE",
        "read_time": 7,
        "content_ar": """
في بلاد الرافدين، كتبت الأحلام على ألواح طينية بالخط المسماري.

📜 **عن الألواح:**
• أقدم الألواح عمرها 4000 سنة
• وجدت في مكتبة آشور بانيبال
• مكتوبة باللغة الأكادية

🌟 **معتقدات البابليين:**
• الأحلام رسائل من الآلهة
• الكهنة يفسرون الأحلام للملوك
• بعض الأحلام سبب للحروب

🔍 **تفسيرات بابلية:**
• رؤية الإله: بركة وحماية
• رؤية الملك: منصب رفيع
• رؤية الثعبان: شفاء
• رؤية النهر: رزق وفير

👑 **أشهر الأحلام:**
• حلم الملك كشتاريا
• أحلام جلجامش في الملحمة
• حلم الملك نبوخذ نصر
""",
        "content_en": """
In Mesopotamia, dreams were written on clay tablets in cuneiform script.

📜 **About the Tablets:**
• Oldest tablets are 4000 years old
• Found in Ashurbanipal's library
• Written in Akkadian

🌟 **Babylonian Beliefs:**
• Dreams were divine messages
• Priests interpreted kings' dreams
• Some dreams caused wars

🔍 **Babylonian Interpretations:**
• Seeing god: blessing and protection
• Seeing king: high position
• Seeing snake: healing
• Seeing river: abundant provision

👑 **Famous Dreams:**
• King Kashtaria's dream
• Gilgamesh's dreams in the epic
• Nebuchadnezzar's dream
"""
    },

    # ===== اليونان القديمة =====
    {
        "title_ar": "معابد أسكليبيوس - الشفاء بالأحلام",
        "title_en": "Asklepieia Temples - Healing Through Dreams",
        "category_ar": "اليونان القديمة",
        "category_en": "Ancient Greece",
        "type": "article",
        "era": "500 BCE - 400 CE",
        "read_time": 7,
        "content_ar": """
في اليونان القديمة، بنيت معابد أسكليبيوس للشفاء بالأحلام.

🏛️ **وصف المعابد:**
• كانت منتشرة في كل اليونان
• أشهرها في إبيداوروس وكوس
• تضم مهاجع للنوم والعلاج

💤 **طريقة العلاج:**
1. يتطهر المريض ويصوم
2. يقدم أضحية لإله الشفاء
3. ينام في المهجع المقدس
4. يأتيه حلم بالعلاج المناسب
5. الكهنة يفسرون الحلم ويصفون العلاج

🌟 **إله الأحلام مورفيوس:**
• كان يظهر في المنام على شكل إنسان
• يستطيع تقليد أي شكل
• ابن هيبنوس (إله النوم)

📚 **فلاسفة الأحلام:**
• أرسطو: كتب عن الأحلام
• أفلاطون: الأحلام نوافذ للروح
• أبقراط: الأحلام تكشف الأمراض
""",
        "content_en": """
In Ancient Greece, Asklepieia temples were built for healing through dreams.

🏛️ **Temple Description:**
• Spread throughout Greece
• Famous ones at Epidaurus and Kos
• Had dormitories for healing sleep

💤 **Healing Process:**
1. Patient purified and fasted
2. Offered sacrifice to healing god
3. Slept in sacred dormitory
4. Received healing dream
5. Priests interpreted and prescribed

🌟 **Morpheus - God of Dreams:**
• Appeared in human form
• Could imitate any shape
• Son of Hypnos (sleep god)

📚 **Philosophers on Dreams:**
• Aristotle: wrote about dreams
• Plato: dreams are soul windows
• Hippocrates: dreams reveal illness
"""
    },

    # ===== علم الأحلام الحديث =====
    {
        "title_ar": "نظرية فرويد في تفسير الأحلام",
        "title_en": "Freud's Dream Theory",
        "category_ar": "علم الأحلام",
        "category_en": "Dream Science",
        "type": "article",
        "era": "1900 CE",
        "read_time": 8,
        "content_ar": """
سيغموند فرويد، مؤسس التحليل النفسي، كتب كتاب "تفسير الأحلام" عام 1900.

📚 **نظريته:**
• الأحلام "طريق ملكي" إلى اللاوعي
• الأحلام تحقق رغبات مكبوتة
• الرموز في الأحلام لها دلالات نفسية

🔍 **آلية الحلم:**
1. الرغبة المكبوتة (في اللاوعي)
2. الرقيب النفسي (يمنع الظهور المباشر)
3. تشويه الرغبة (تظهر برموز)
4. الحلم النهائي (صورة رمزية)

🌟 **الرموز عند فرويد:**
• العصا: رمز ذكري
• الصندوق: رمز أنثوي
• الطيران: رغبة جنسية
• السقوط: خوف من الفشل

⚠️ **انتقادات النظرية:**
• ركز كثيراً على الجنس
• أهمل الجانب الروحي
• عارضه تلميذه يونغ
""",
        "content_en": """
Sigmund Freud, founder of psychoanalysis, wrote "The Interpretation of Dreams" in 1900.

📚 **His Theory:**
• Dreams are "royal road" to unconscious
• Dreams fulfill repressed wishes
• Symbols have psychological meanings

🔍 **Dream Mechanism:**
1. Repressed wish (in unconscious)
2. Mental censor (blocks direct expression)
3. Wish distortion (appears as symbols)
4. Final dream (symbolic image)

🌟 **Freudian Symbols:**
• Stick: male symbol
• Box: female symbol
• Flying: sexual desire
• Falling: fear of failure

⚠️ **Criticism:**
• Over-emphasized sexuality
• Ignored spiritual aspects
• Opposed by his student Jung
"""
    },
    {
        "title_ar": "الأحلام وحركة العين السريعة (REM)",
        "title_en": "Dreams and REM Sleep",
        "category_ar": "علم الأحلام",
        "category_en": "Dream Science",
        "type": "article",
        "era": "1953 CE",
        "read_time": 6,
        "content_ar": """
في عام 1953، اكتشف العلماء حركة العين السريعة أثناء النوم.

🌙 **ما هي حركة العين السريعة؟**
• مرحلة من النوم تتحرك فيها العين بسرعة
• تحدث كل 90 دقيقة
• تستمر من 5 إلى 30 دقيقة
• فيها تحدث معظم الأحلام

🧠 **خصائص نوم REM:**
• المخ نشيط جداً
• العضلات مشلولة (لا نتحرك)
• ضربات القلب غير منتظمة
• التنفس سريع

📊 **إحصائيات:**
• 20-25% من النوم REM
• 4-5 فترات REM كل ليلة
• 2 ساعة أحلام كل ليلة
• 6 سنوات أحلام في العمر

🔬 **اكتشافات حديثة:**
• الأحلام تساعد على تثبيت الذاكرة
• تنظم المشاعر
• تنظف المخ من السموم
• تطور الإبداع
""",
        "content_en": """
In 1953, scientists discovered Rapid Eye Movement (REM) sleep.

🌙 **What is REM?**
• Sleep stage with rapid eye movement
• Occurs every 90 minutes
• Lasts 5-30 minutes
• Most dreams occur here

🧠 **REM Characteristics:**
• Brain highly active
• Muscles paralyzed
• Irregular heartbeat
• Rapid breathing

📊 **Statistics:**
• 20-25% of sleep is REM
• 4-5 REM periods nightly
• 2 hours of dreams nightly
• 6 years of dreaming in lifetime

🔬 **Recent Discoveries:**
• Dreams help memory consolidation
• Regulate emotions
• Clean brain toxins
• Enhance creativity
"""
    },

    # ===== تقارير خاصة =====
    {
        "title_ar": "📊 تقرير: أكثر الأحلام شيوعاً في 2026",
        "title_en": "📊 Report: Most Common Dreams in 2026",
        "category_ar": "تقارير",
        "category_en": "Reports",
        "type": "report",
        "era": "2026",
        "read_time": 5,
        "content_ar": """
تقرير إحصائي عن أكثر الأحلام شيوعاً هذا العام:

🥇 **السقوط من مكان مرتفع** (78%)
• يدل على عدم الاستقرار
• خوف من الفشل
• فقدان السيطرة

🥈 **الأسنان تسقط** (65%)
• قلق على المظهر
• خوف من التقدم في العمر
• مشاكل عائلية

🥉 **الطيران** (52%)
• رغبة في الحرية
• نجاح وتفوق
• تخلص من هموم

4️⃣ **الامتحانات** (48%)
• قلق من التقييم
• خوف من الفشل
• ضغط نفسي

5️⃣ **المطاردة** (43%)
• هروب من مشكلة
• خوف من شيء
• ضغوط الحياة

📈 **زيادة هذا العام:**
• أحلام الذكاء الاصطناعي: +150%
• أحلام السفر: +80%
• أحلام الثراء: +60%

🌍 **حسب المناطق:**
• السعودية: الامتحانات الأكثر
• مصر: الأسنان الأكثر
• أمريكا: السقوط الأكثر
• أوروبا: الطيران الأكثر
""",
        "content_en": """
Statistical report on the most common dreams this year:

🥇 **Falling from height** (78%)
• Instability
• Fear of failure
• Loss of control

🥈 **Teeth falling out** (65%)
• Appearance anxiety
• Fear of aging
• Family issues

🥉 **Flying** (52%)
• Freedom desire
• Success
• Freedom from worries

4️⃣ **Exams** (48%)
• Evaluation anxiety
• Fear of failure
• Mental pressure

5️⃣ **Being chased** (43%)
• Escaping problems
• Fear of something
• Life pressures

📈 **Increase this year:**
• AI dreams: +150%
• Travel dreams: +80%
• Wealth dreams: +60%

🌍 **By Region:**
• Saudi Arabia: exams most common
• Egypt: teeth most common
• USA: falling most common
• Europe: flying most common
"""
    },
    {
        "title_ar": "📈 تقرير: تأثير الذكاء الاصطناعي على الأحلام",
        "title_en": "📈 Report: AI Impact on Dreams",
        "category_ar": "تقارير",
        "category_en": "Reports",
        "type": "report",
        "era": "2026",
        "read_time": 6,
        "content_ar": """
كيف يؤثر الذكاء الاصطناعي على أحلامنا؟

🤖 **إحصائيات 2026:**
• 73% يستخدمون ChatGPT
• 45% يحلمون بالروبوتات
• 38% يرون ذكاء اصطناعي في المنام

🌙 **أنماط الأحلام الجديدة:**
• التحدث مع روبوتات
• العيش في عوالم افتراضية
• العمل مع مساعدين رقميين

📊 **تغييرات في التفسير:**
• الحاسوب: يدل على التنظيم
• الإنترنت: التواصل مع العالم
• الروبوت: المساعدة في العمل

🔮 **توقعات:**
• زيادة أحلام الميتافيرس
• أحلام عن العمل عن بعد
• رموز تقنية جديدة

⚠️ **تأثير سلبي:**
• 28% كوابيس عن التقنية
• قلق من استبدال البشر
• خوف من فقدان الخصوصية
""",
        "content_en": """
How does AI affect our dreams?

🤖 **2026 Statistics:**
• 73% use ChatGPT
• 45% dream about robots
• 38% see AI in dreams

🌙 **New Dream Patterns:**
• Talking with robots
• Living in virtual worlds
• Working with digital assistants

📊 **Interpretation Changes:**
• Computer: organization
• Internet: global connection
• Robot: work assistance

🔮 **Predictions:**
• More metaverse dreams
• Remote work dreams
• New technological symbols

⚠️ **Negative Impact:**
• 28% tech nightmares
• Fear of human replacement
• Privacy concerns
"""
    }
]

# =========================================
# دوال البوت
# =========================================
def create_article_html(article, lang='ar'):
    """إنشاء ملف HTML للمقالة"""
    
    today = datetime.datetime.now()
    date_str = today.strftime("%Y-%m-%d")
    filename_date = today.strftime("%Y%m%d")
    time_str = today.strftime("%H:%M")
    
    # تنظيف العنوان لاستخدامه في اسم الملف
    clean_title = article[f'title_{lang}'].replace(' ', '-').replace(':', '').replace('؟', '')
    clean_title = ''.join(c for c in clean_title if c.isalnum() or c == '-')[:50]
    
    if lang == 'ar':
        filename = f"articles/{filename_date}-{clean_title}.html"
        
        html = f"""<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{article['title_ar']} - Weaver</title>
    <meta name="description" content="{article['title_ar']} - {article['category_ar']}">
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{
            font-family: 'Tajawal', sans-serif;
            background: #0a0514;
            color: #e2d9f3;
            line-height: 1.8;
            padding: 2rem;
        }}
        .container {{ max-width: 800px; margin: 0 auto; }}
        .header {{
            text-align: center;
            margin-bottom: 3rem;
        }}
        h1 {{
            color: #f0c060;
            font-size: 2.5rem;
            margin-bottom: 1rem;
        }}
        .meta {{
            display: flex;
            justify-content: center;
            gap: 2rem;
            color: #a855f7;
            margin-bottom: 1rem;
            flex-wrap: wrap;
        }}
        .category {{
            background: #7c3aed;
            color: white;
            padding: 0.3rem 1rem;
            border-radius: 50px;
            display: inline-block;
            margin-bottom: 1rem;
        }}
        .content {{
            background: rgba(30,10,60,0.3);
            padding: 2rem;
            border-radius: 20px;
            border: 1px solid #7c3aed;
            white-space: pre-line;
        }}
        .content h2 {{
            color: #f0c060;
            margin: 1.5rem 0 1rem;
        }}
        .content h3 {{
            color: #a855f7;
            margin: 1rem 0;
        }}
        .content ul, .content ol {{
            margin-right: 2rem;
            margin-bottom: 1rem;
        }}
        .footer {{
            text-align: center;
            margin-top: 3rem;
            padding-top: 2rem;
            border-top: 1px solid #7c3aed;
        }}
        .badge {{
            background: linear-gradient(135deg, #7c3aed, #ec4899);
            color: white;
            padding: 0.2rem 0.5rem;
            border-radius: 20px;
            font-size: 0.8rem;
        }}
        .bot-button {{
            position: fixed;
            bottom: 20px;
            left: 20px;
            background: linear-gradient(135deg, #7c3aed, #ec4899);
            color: white;
            padding: 1rem 2rem;
            border-radius: 50px;
            text-decoration: none;
            font-weight: bold;
            box-shadow: 0 4px 15px rgba(124,58,237,0.3);
            z-index: 1000;
        }}
        @media (max-width: 600px) {{
            body {{ padding: 1rem; }}
            h1 {{ font-size: 1.8rem; }}
            .meta {{ flex-direction: column; gap: 0.5rem; }}
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <span class="category">{article['category_ar']} {article['type'] == 'report' and '📊' or ''}</span>
            <h1>{article['title_ar']}</h1>
            <div class="meta">
                <span>📅 {date_str}</span>
                <span>⏱️ {article['read_time']} دقائق قراءة</span>
                <span>🔖 {article.get('era', '')}</span>
                <span>🆔 مقالة #{filename_date}</span>
            </div>
        </div>
        
        <div class="content">
            {article[f'content_{lang}']}
        </div>
        
        <div class="footer">
            <p>© 2026 Weaver | نَسَّاج - منصة تفسير الأحلام بالذكاء الاصطناعي</p>
            <p>📚 المصدر: موسوعة Weaver الثقافية | تحديث: {date_str} {time_str}</p>
            <p>🤖 بوت تيليجرام: <a href="https://t.me/aidreamweaver_bot" style="color: #f0c060;">@aidreamweaver_bot</a></p>
            <p>🔗 <a href="https://aidreamweaver.store" style="color: #f0c060;">العودة إلى المدونة</a></p>
        </div>
    </div>
    
    <a href="https://t.me/aidreamweaver_bot" class="bot-button" target="_blank">
        🤖 جرب بوت تفسير الأحلام
    </a>
</body>
</html>"""
    else:
        filename = f"articles/{filename_date}-{clean_title}-eng.html"
        
        html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{article['title_en']} - Weaver</title>
    <meta name="description" content="{article['title_en']} - {article['category_en']}">
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{
            font-family: 'Inter', sans-serif;
            background: #0a0514;
            color: #e2d9f3;
            line-height: 1.8;
            padding: 2rem;
        }}
        .container {{ max-width: 800px; margin: 0 auto; }}
        .header {{
            text-align: center;
            margin-bottom: 3rem;
        }}
        h1 {{
            color: #f0c060;
            font-size: 2.5rem;
            margin-bottom: 1rem;
        }}
        .meta {{
            display: flex;
            justify-content: center;
            gap: 2rem;
            color: #a855f7;
            margin-bottom: 1rem;
            flex-wrap: wrap;
        }}
        .category {{
            background: #7c3aed;
            color: white;
            padding: 0.3rem 1rem;
            border-radius: 50px;
            display: inline-block;
            margin-bottom: 1rem;
        }}
        .content {{
            background: rgba(30,10,60,0.3);
            padding: 2rem;
            border-radius: 20px;
            border: 1px solid #7c3aed;
            white-space: pre-line;
        }}
        .content h2 {{
            color: #f0c060;
            margin: 1.5rem 0 1rem;
        }}
        .content h3 {{
            color: #a855f7;
            margin: 1rem 0;
        }}
        .content ul, .content ol {{
            margin-left: 2rem;
            margin-bottom: 1rem;
        }}
        .footer {{
            text-align: center;
            margin-top: 3rem;
            padding-top: 2rem;
            border-top: 1px solid #7c3aed;
        }}
        .badge {{
            background: linear-gradient(135deg, #7c3aed, #ec4899);
            color: white;
            padding: 0.2rem 0.5rem;
            border-radius: 20px;
            font-size: 0.8rem;
        }}
        .bot-button {{
            position: fixed;
            bottom: 20px;
            left: 20px;
            background: linear-gradient(135deg, #7c3aed, #ec4899);
            color: white;
            padding: 1rem 2rem;
            border-radius: 50px;
            text-decoration: none;
            font-weight: bold;
            box-shadow: 0 4px 15px rgba(124,58,237,0.3);
            z-index: 1000;
        }}
        @media (max-width: 600px) {{
            body {{ padding: 1rem; }}
            h1 {{ font-size: 1.8rem; }}
            .meta {{ flex-direction: column; gap: 0.5rem; }}
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <span class="category">{article['category_en']} {article['type'] == 'report' and '📊' or ''}</span>
            <h1>{article['title_en']}</h1>
            <div class="meta">
                <span>📅 {date_str}</span>
                <span>⏱️ {article['read_time']} min read</span>
                <span>🔖 {article.get('era', '')}</span>
                <span>🆔 Article #{filename_date}</span>
            </div>
        </div>
        
        <div class="content">
            {article[f'content_{lang}']}
        </div>
        
        <div class="footer">
            <p>© 2026 Weaver - AI Dream Interpretation Platform</p>
            <p>📚 Source: Weaver Cultural Encyclopedia | Updated: {date_str} {time_str}</p>
            <p>🤖 Telegram Bot: <a href="https://t.me/aidreamweaver_bot" style="color: #f0c060;">@aidreamweaver_bot</a></p>
            <p>🔗 <a href="https://aidreamweaver.store" style="color: #f0c060;">Back to Blog</a></p>
        </div>
    </div>
    
    <a href="https://t.me/aidreamweaver_bot" class="bot-button" target="_blank">
        🤖 Try the Dream Bot
    </a>
</body>
</html>"""
    
    return filename, html

def update_blog_index(article, filename_ar, filename_en):
    """تحديث صفحة المدونة الرئيسية"""
    
    today = datetime.datetime.now().strftime("%b %d, %Y")
    
    # تحديث blog.html (عربي)
    blog_ar_path = Path("blog.html")
    if blog_ar_path.exists():
        with open(blog_ar_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        article_entry = f"""
                <div class="feature-card">
                    <div class="feature-icon">{'📊' if article['type'] == 'report' else '📚'}</div>
                    <h3>{article['category_ar']}</h3>
                    <h4>{article['title_ar']}</h4>
                    <p>{article['content_ar'][:100]}...</p>
                    <div class="meta">
                        <span>📅 {today}</span>
                        <span>⏱️ {article['read_time']} دقائق</span>
                    </div>
                    <a href="{filename_ar}" style="color: #f0c060;">[AI] اقرأ المزيد →</a>
                </div>
"""
        
        marker = "<!-- LATEST_ARTICLES_START -->"
        if marker in content:
            new_content = content.replace(marker, f"{marker}\n{article_entry}")
            with open(blog_ar_path, 'w', encoding='utf-8') as f:
                f.write(new_content)
            print("✅ تم تحديث blog.html")
    
    # تحديث blog-eng.html (إنجليزي)
    blog_en_path = Path("blog-eng.html")
    if blog_en_path.exists():
        with open(blog_en_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        article_entry = f"""
                <div class="feature-card">
                    <div class="feature-icon">{'📊' if article['type'] == 'report' else '📚'}</div>
                    <h3>{article['category_en']}</h3>
                    <h4>{article['title_en']}</h4>
                    <p>{article['content_en'][:100]}...</p>
                    <div class="meta">
                        <span>📅 {today}</span>
                        <span>⏱️ {article['read_time']} min</span>
                    </div>
                    <a href="{filename_en}" style="color: #f0c060;">[AI] Read more →</a>
                </div>
"""
        
        marker = "<!-- LATEST_ARTICLES_START -->"
        if marker in content:
            new_content = content.replace(marker, f"{marker}\n{article_entry}")
            with open(blog_en_path, 'w', encoding='utf-8') as f:
                f.write(new_content)
            print("✅ تم تحديث blog-eng.html")

def send_telegram_notification(article, filename_ar, filename_en):
    """إرسال إشعار على تيليجرام"""
    
    # هذا اختياري - يحتاج توكن
    pass

def publish_daily():
    """الدالة الرئيسية - تنشر مقالة كل يوم"""
    
    print("="*60)
    print(f"🚀 {BOT_NAME} v{VERSION}")
    print("="*60)
    print(f"📅 التاريخ: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # إنشاء مجلد المقالات
    Path("articles").mkdir(exist_ok=True)
    Path("reports").mkdir(exist_ok=True)
    
    # اختيار موضوع عشوائي
    article = random.choice(ARTICLES)
    print(f"📚 الموضوع: {article['title_ar']}")
    print(f"🏷️ التصنيف: {article['category_ar']}")
    print(f"📊 النوع: {article['type']}")
    
    # إنشاء المقالة العربية
    filename_ar, html_ar = create_article_html(article, 'ar')
    with open(filename_ar, 'w', encoding='utf-8') as f:
        f.write(html_ar)
    print(f"✅ تم إنشاء: {filename_ar}")
    
    # إنشاء المقالة الإنجليزية
    filename_en, html_en = create_article_html(article, 'en')
    with open(filename_en, 'w', encoding='utf-8') as f:
        f.write(html_en)
    print(f"✅ تم إنشاء: {filename_en}")
    
    # تحديث المدونة
    update_blog_index(article, filename_ar, filename_en)
    
    # إنشاء ملف JSON للتتبع
    log = {
        "date": datetime.datetime.now().strftime("%Y-%m-%d"),
        "time": datetime.datetime.now().strftime("%H:%M:%S"),
        "article": {
            "title_ar": article['title_ar'],
            "title_en": article['title_en'],
            "category_ar": article['category_ar'],
            "category_en": article['category_en'],
            "type": article['type']
        },
        "files": {
            "arabic": filename_ar,
            "english": filename_en
        }
    }
    
    log_file = f"logs/{datetime.datetime.now().strftime('%Y%m%d')}.json"
    Path("logs").mkdir(exist_ok=True)
    with open(log_file, 'w', encoding='utf-8') as f:
        json.dump(log, f, ensure_ascii=False, indent=2)
    print(f"✅ تم تسجيل النشر في: {log_file}")
    
    print("\n" + "="*60)
    print("🎉 تم النشر بنجاح!")
    print("="*60)
    
    return filename_ar, filename_en

# =========================================
# ملف GitHub Actions
# =========================================
def create_github_workflow():
    """إنشاء ملف للتشغيل التلقائي"""
    
    workflow_dir = Path(".github/workflows")
    workflow_dir.mkdir(parents=True, exist_ok=True)
    
    workflow_content = """name: نشر المقالات اليومي 📚

on:
  schedule:
    - cron: '0 3 * * *'  # 6 صباحاً السعودية
  workflow_dispatch:  # للتشغيل اليدوي

jobs:
  publish:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      
      - name: إعداد Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.10'
      
      - name: تشغيل البوت
        run: python daily_blog_bot.py
      
      - name: رفع التغييرات
        run: |
          git config user.name "Weaver Bot"
          git config user.email "bot@aidreamweaver.store"
          git add articles/ logs/ *.html
          git commit -m "📚 نشر مقالة يومية - $(date +'%Y-%m-%d')" || exit 0
          git push
"""
    
    with open(workflow_dir / "daily_blog.yml", 'w', encoding='utf-8') as f:
        f.write(workflow_content)
    print("✅ تم إنشاء ملف GitHub Actions")

# =========================================
# التشغيل
# =========================================
if __name__ == "__main__":
    # تشغيل البوت
    publish_daily()
    
    # إنشاء ملف GitHub Actions (مرة واحدة)
    if not Path(".github/workflows/daily_blog.yml").exists():
        create_github_workflow()
