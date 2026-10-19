# sheet-snapshot

Claude Code plugin: snapshot ไฟล์ Excel (.xlsx/.csv) หรือ Google Sheet เป็นหน้า HTML ไฟล์เดียว
ที่แสดงข้อมูล และให้ upload ไฟล์รุ่นใหม่มาเทียบ diff ราย cell (แถวเพิ่ม / ลบ / แก้ไข) ใน browser ได้เลย

## ติดตั้ง
```bash
claude plugin marketplace add <git-url-ของ-repo-นี้>
```
แล้วใน `claude` พิมพ์ `/plugin install sheet-snapshot@sheet-snapshot-local`

## ใช้งาน
บอก Claude เช่น "snapshot ไฟล์ report.xlsx ให้หน่อย" หรือ "snapshot แล้วขอลิงก์ไว้แชร์ทีม"
(ก่อน publish จะถามเสมอว่าอัปเดตลิงก์เดิมหรือสร้างลิงก์ใหม่)

รัน script ตรง ๆ ก็ได้ (Python 3 standard library ล้วน):
```bash
python3 skills/sheet-snapshot/scripts/snapshot.py input.xlsx -o out.html --key "ID"
```

## โครงสร้าง
- `skills/sheet-snapshot/SKILL.md`: ขั้นตอนที่ Claude ทำตาม
- `skills/sheet-snapshot/scripts/snapshot.py`: แปลงไฟล์เป็น HTML
- `skills/sheet-snapshot/assets/template.html`: หน้าแสดงผล + upload + diff
- `skills/sheet-snapshot/evals/evals.json` และ `skills/sheet-snapshot-workspace/inputs/`: โจทย์ทดสอบ (ข้อมูลสมมติ)
