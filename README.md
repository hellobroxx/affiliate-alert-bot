# Affiliate Alert Bot - v1 - Setup Guide (Easy Steps)

Tumne Affiliate chuna hai, isliye ye bot ban gaya hai. Ye Rs 0 se chalega.

## Ye bot kya karega
- User: /start, /deals, /track, /coupon
- Admin (tum): /postdeal se deal post karoge, bot usko channel pe "Affiliate Link" disclosure ke saath bhejega
- EarnKaro se Profit Link tumhe app me banana hai, bot us link ko hi share karega. Bot khud EarnKaro link nahi banata.

## Tumhe kya karna hai - 4 kaam

### 1. Telegram Bot banao (5 min)
1. Telegram me @BotFather ko kholo
2. /newbot bhejo, bot ka naam do, jaise `DealLootAlertBot`
3. Jo token milega, usko safe rakho. Token chat me mat bhejo, mujhe secure tarike se doge to main deploy kar dunga.

### 2. Telegram Channel banao (5 min)
1. Ek public channel banao, jaise `@TumharaDealChannel`
2. Apne bot ko channel me Admin banao (Post Messages ka permission deke)
3. Channel ka username note karo - yehi CHANNEL_ID hoga

### 3. Apna Telegram ID nikalo (2 min)
1. Telegram me @userinfobot ko /start bhejo
2. Jo ID milegi, wohi ADMIN_ID hogi

### 4. EarnKaro account banao (10 min)
1. EarnKaro app download karo, free signup karo
2. Bank details daalo (payout ke liye)
3. Kisi product ka link copy karo -> EarnKaro me Make Link -> Profit Link ban jayega
4. Wahi Profit Link /postdeal me paste karna hai

## Bot ko chalana (Main kar dunga, tumhe bas token dena hai)
- Render free pe deploy hoga. Render free 15 min bina traffic ke so jata hai, pehla reply 1 min late aa sakta hai. Ye normal hai.
- Database abhi SQLite hai. Render restart pe purana data reset ho sakta hai. v2 me Supabase free DB lagayenge.

## Roz ka kaam - tumhara
- Din me 5-10 best deal hi post karo, 100 mat bhejo
- Har post me bot khud "Affiliate Link" likh dega, tumhe alag se nahi likhna
- Deal post karne ka format:
  `/postdeal Boat Earbuds | 499 | 999 | https://earnkaro.com/... | electronics`
- Amazon ka rule yaad rakho: 180 din me 3 sale nahi aayi to Amazon account band ho jayega, isliye pehle EarnKaro se shuru karo, Amazon baad me.

## Pehla test
1. Bot ko /start bhejo
2. /postdeal se ek test deal post karo (apna hi EarnKaro link)
3. /deals se check karo ki deal dikh rahi hai ya nahi

## Niche abhi tay nahi hai
Bot kisi bhi niche pe chalega - Tech, Fashion, Student Deals, Home. Batao kaun sa niche rakhna hai, to main /start message aur channel description us hisab se set kar dunga.
