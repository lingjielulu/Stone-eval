# Short Story CFPG Candidate Review

## Candidates

### medicine:ftp_candidate:000001

- Type: `symbolic` / payoff `negative`
- Distance: 42 paragraphs
- F P0012-P0014: 華老栓用洋錢買到一個蘸著鮮血的饅頭，視之為能帶給小栓新生命的藥。
- T: 茶館裡康大叔吹噓人血饅頭「包好」時，小栓在裏屋合夥咳嗽，顯示饅頭並未見效。
- P P0054-P0057: 清明時節，華大媽在小栓墳前祭奠，揭示小栓已死，人血饅頭未能治好他的癆病。
- Rationale: 從購買饅頭到死亡結果，中間有明確的無效跡象（持續咳嗽）和最終悲劇，間隔長，回收完整。

### medicine:ftp_candidate:000002

- Type: `social` / payoff `symbolic`
- Distance: 22 paragraphs
- F P0038-P0047: 茶客們把夏瑜視為不要命的瘋子，對其革命行動充滿誤解與鄙夷。
- T: 夏四奶奶與華大媽發現夏瑜墳頂有一圈紅白的花。
- P P0060-P0062: 夏瑜墳上出現紅白花環，夏四奶奶哭訴兒子被冤枉，暗示有人理解夏瑜，為被誤解的革命者留下象徵性悼念。
- Rationale: 茶客對話與墳場花環形成強烈反差，花環作為象徵性回收，非相鄰段落，符合延遲揭示。

### medicine:ftp_candidate:000003

- Type: `spatial` / payoff `delayed_revelation`
- Distance: 32 paragraphs
- F P0006-P0011: 老栓在丁字街口看到清兵與古怪的人群，氣氛陰森，暗示此處為行刑地點。
- T: 康大叔來到茶館，高聲談論早晨處決的犯人是夏家的孩子，並細說夏瑜在獄中的行為。
- P P0038-P0041: 茶館談話揭示早晨處決的是革命者夏瑜，說明之前老栓所見的正是夏瑜被殺的場景。
- Rationale: 從環境鋪墊到人物身份揭露，間隔多個段落，且非即時因果，構成有效的延遲揭示結構。

## Verification

### medicine:ftp_candidate:000001

- accepted: `False`
- rationale: 候選觸發事件（茶館中康大叔吹噓與小栓咳嗽）發生於購買饅頭之後，雖然顯示饅頭可能無效，但無法解釋清明上墳場景（payoff）的時機，即無法說明為何在此刻發生回收。觸發事件與payoff之間缺少直接因果或時序聯繫，不符合 trigger 須能解釋 payoff 時機的要求。
- rejection: Trigger does not justify the timing of the payoff; the coughing scene does not directly explain why the grave scene occurs at Qingming.

### medicine:ftp_candidate:000002

- accepted: `True`
- rationale: F 引入夏瑜事件但未详尽；P 用花环意象具体暗示革命者仍有同情者，回收了 F 中社会对夏瑜误解的伏笔，构成真实叙事回收。
- rejection: 

### medicine:ftp_candidate:000003

- accepted: `True`
- rationale: 早期對刑場環境的描寫（F）在後文透過康大叔的對話（P）得到解釋，明確老栓購買人血饅頭的過程，構成典型的伏筆與回收關係。F引入未解釋的敘事元素，P提供新資訊履行並回顧性重釋F，時間有間隔，觸發事件可觀察，非僅主題呼應。
- rejection: 
