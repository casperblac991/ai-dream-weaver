class DataManager:
    """إدارة البيانات بشكل آمن"""
    def __init__(self, data_file='data.json'):
        self.data_file = data_file
        self.data = self.load_data()
    
    def load_data(self):
        """تحميل البيانات من الملف"""
        try:
            if os.path.exists(self.data_file):
                with open(self.data_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            return {'users': [], 'stats': {'total_users': 0, 'total_requests': 0}}
        except Exception as e:
            print(f"خطأ في تحميل البيانات: {e}")
            return {'users': [], 'stats': {'total_users': 0, 'total_requests': 0}}
    
    def save_data(self):
        """حفظ البيانات في الملف"""
        try:
            with open(self.data_file, 'w', encoding='utf-8') as f:
                json.dump(self.data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"خطأ في حفظ البيانات: {e}")
    
    def get_stats(self):
        """جلب الإحصائيات بشكل آمن"""
        try:
            if 'stats' not in self.data:
                self.data['stats'] = {'total_users': 0, 'total_requests': 0}
            
            # تحديث عدد المستخدمين
            if 'users' in self.data:
                self.data['stats']['total_users'] = len(self.data['users'])
            
            return self.data['stats']
        except Exception as e:
            print(f"خطأ في جلب الإحصائيات: {e}")
            return {'total_users': 0, 'total_requests': 0}
    
    def add_user(self, user_id, source):
        """إضافة مستخدم جديد"""
        try:
            if 'users' not in self.data:
                self.data['users'] = []
            
            # نتأكد إن المستخدم مش مكرر
            for user in self.data['users']:
                if user.get('id') == user_id:
                    return
            
            # نضيف المستخدم الجديد
            self.data['users'].append({
                'id': user_id,
                'source': source,
                'first_seen': datetime.now().isoformat(),
                'last_seen': datetime.now().isoformat(),
                'requests_count': 0
            })
            
            self.save_data()
            print(f"✅ تم حفظ عميل جديد من {source}: {user_id}")
            
        except Exception as e:
            print(f"خطأ في إضافة المستخدم: {e}")
