# sheet-snapshot

Claude Code plugin: snapshot ไฟล์ Excel (.xlsx/.csv) หรือ Google Sheet เป็นหน้า HTML ไฟล์เดียว
ที่แสดงข้อมูล และให้ upload ไฟล์รุ่นใหม่มาเทียบ diff ราย cell (แถวเพิ่ม / ลบ / แก้ไข) ใน browser ได้เลย

## ติดตั้ง

ติดตั้งครั้งเดียว ใช้ได้ทั้ง Claude Code ใน terminal และแท็บ **Code** ของ Claude Desktop
(ทั้งสองที่ใช้ plugin ชุดเดียวกันใน `~/.claude`)

รันใน terminal:
```bash
claude plugin marketplace add Panarin-U/sheet-snapshot-plugin
```
```bash
claude plugin install sheet-snapshot@sheet-snapshot-local
```

หรือถ้าอยู่ใน `claude` แบบ interactive อยู่แล้ว พิมพ์ `/plugin install sheet-snapshot@sheet-snapshot-local`
แทนคำสั่งที่สองได้

ถ้า repo เป็น private ต้องมีสิทธิ์เข้าถึง repo บน GitHub ก่อน

## ใช้งานใน Claude Desktop

1. เปิด Claude Desktop แล้วไปที่แท็บ **Code**
2. เริ่ม session ใหม่ เลือกโฟลเดอร์ที่จะเก็บไฟล์ snapshot (ไฟล์ HTML จะถูกสร้างในโฟลเดอร์นั้น)
3. ชี้ไฟล์ Excel ให้ Claude ได้ 2 วิธี
   - พิมพ์ `@` แล้วตามด้วย path ของไฟล์ เช่น `@"/Users/<you>/Downloads/report.xlsx"`
   - ลากไฟล์จาก Finder มาวางในช่องพิมพ์
4. สั่งงาน เลือกได้ 2 แบบ
   - เรียก skill ตรง ๆ: `/sheet-snapshot:sheet-snapshot` ต่อท้ายไฟล์ที่แนบ
   - พิมพ์บอกธรรมดา เช่น "snapshot ไฟล์นี้ให้หน่อย จะเอาไว้เทียบรอบหน้า"
5. Claude จะสร้าง HTML แล้วถามว่าจะ publish ไหม มี 3 ตัวเลือก
   - **สร้างลิงก์ใหม่**: ได้ลิงก์ claude.ai ที่ยังเป็น private อยู่
   - **อัปเดตลิงก์เดิม**: ส่ง URL เดิมให้ Claude แล้วจะเขียนทับที่ลิงก์เดิม ต้องมีสิทธิ์ Editor ของลิงก์นั้น
   - **ไม่ publish**: ใช้ไฟล์ HTML ในเครื่องอย่างเดียว
6. ถ้า publish แล้ว ให้กด **Share** บนหน้านั้นเพื่อเลือกคนที่จะเห็น
7. ตอนเทียบ ให้เปิดหน้า snapshot แล้วลากไฟล์รุ่นใหม่มาวาง จะเห็นแถวที่เพิ่ม ลบ และ cell ที่แก้ไข

ถ้าไฟล์เป็น Google Sheet ให้วางลิงก์ Google Sheet แทนไฟล์ได้เลย ต้องเชื่อม Google Drive connector ไว้ก่อน

## ใช้งานใน terminal

ในโฟลเดอร์ที่ต้องการ รัน `claude` แล้วสั่งงานแบบเดียวกับข้างบน เช่น
"snapshot ไฟล์ report.xlsx ให้หน่อย" หรือ `/sheet-snapshot:sheet-snapshot`

หรือรัน script ตรง ๆ โดยไม่ผ่าน Claude ก็ได้ (Python 3 standard library ล้วน):
```bash
python3 skills/sheet-snapshot/scripts/snapshot.py input.xlsx -o out.html --key "ID"
```

## อัปเดต plugin

```bash
claude plugin marketplace update sheet-snapshot-local
```
```bash
claude plugin update sheet-snapshot@sheet-snapshot-local
```
จากนั้นเริ่ม session ใหม่ (ใน Claude Desktop ให้เปิด session ใหม่ในแท็บ Code)

## โครงสร้าง
- `skills/sheet-snapshot/SKILL.md`: ขั้นตอนที่ Claude ทำตาม
- `skills/sheet-snapshot/scripts/snapshot.py`: แปลงไฟล์เป็น HTML
- `skills/sheet-snapshot/assets/template.html`: หน้าแสดงผล + upload + diff
- `skills/sheet-snapshot/evals/`: โจทย์ทดสอบ (`evals.json`) และผล eval (`RESULTS.md`)
- `skills/sheet-snapshot-workspace/inputs/`: ไฟล์ทดสอบ (ข้อมูลสมมติ)
