def calculate_sleep_score(SD, AR, SP, SE):
    # 睡眠时间太短，不予评分
    if SD < 30:
        return -1
    
    # 计算SD-Score (满分50分)
    if SD >= 7 * 60:  # 转换为分钟
        SD_Score = 50
    else:
        SD_Score = 50 * (SD / (7 * 60))
    
    # 计算AR-Score (满分20分)
    if AR <= 20:
        AR_Score = 20
    elif 20 < AR <= 40:
        AR_Score = 15
    elif 40 < AR <= 60:
        AR_Score = 10
    else:
        AR_Score = 5
    
    # 计算SP-Score (满分20分)
    if SP < 20:
        SP_Score = 20
    elif 20 <= SP < 40:
        SP_Score = 20 * 0.8
    elif 40 <= SP < 60:
        SP_Score = 20 * 0.5
    elif 60 <= SP < 90:
        SP_Score = 20 * 0.4
    else:
        SP_Score = 20 * 0.2
    
    # 计算SE-Score (满分10分)
    SE_Score = 10 * SE
    
    # 计算总分
    total_score = SD_Score + AR_Score + SP_Score + SE_Score
    
    return total_score