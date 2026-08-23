---
id: scl90
name: 症状自评量表 (SCL-90)
version: 1.0
description: |
  评估过去一周内心理症状的严重程度，包含90个项目，采用0-4级评分。
  计算9个因子均分（原始分/题数）及总分（0-360）。
  总分>160或阳性项目数>43提示阳性症状；任一因子均分≥2提示该维度存在轻度及以上困扰。
time_reference: 过去一周内（包括今天）

dimensions:
  - name: total
    items: "1-90"                # 所有题号，解析时展开为1..90
    weight: 1
  - name: somatization
    items: [1, 4, 12, 27, 40, 42, 48, 49, 52, 53, 56, 58]
    weight: 1
    value_type: mean
  - name: obsessive_compulsive
    items: [3, 9, 10, 28, 38, 45, 46, 51, 55, 65]
    weight: 1
    value_type: mean
  - name: interpersonal_sensitivity
    items: [6, 21, 34, 36, 37, 41, 61, 69, 73]
    weight: 1
    value_type: mean
  - name: depression
    items: [5, 14, 15, 20, 22, 26, 29, 30, 31, 32, 54, 71, 79]
    weight: 1
    value_type: mean
  - name: anxiety
    items: [2, 17, 23, 33, 39, 57, 72, 78, 80, 86]
    weight: 1
    value_type: mean
  - name: hostility
    items: [11, 24, 63, 67, 74, 81]
    weight: 1
    value_type: mean
  - name: phobic_anxiety
    items: [13, 25, 47, 50, 70, 75, 82]
    weight: 1
    value_type: mean
  - name: paranoid_ideation
    items: [8, 18, 43, 68, 76, 83]
    weight: 1
    value_type: mean
  - name: psychoticism
    items: [7, 16, 35, 62, 77, 84, 85, 87, 88, 90]
    weight: 1
    value_type: mean

scoring:
  total:
    - range: [0, 160]
      level: 正常
      description: 总分在正常范围内，无阳性症状
    - range: [161, 360]
      level: 阳性
      description: 总分超过160分，提示可能存在心理困扰，建议进一步评估
  somatization:
    - range: [0, 1.99]
      level: 正常
      description: 躯体化症状在正常范围
    - range: [2, 2.99]
      level: 轻度
      description: 轻度躯体化倾向，建议自我关注
    - range: [3, 3.99]
      level: 中度
      description: 中度躯体化倾向，建议寻求专业咨询
    - range: [4, 4]
      level: 重度
      description: 重度躯体化倾向，强烈建议精神科就诊
  obsessive_compulsive:
    - range: [0, 1.99]
      level: 正常
      description: 强迫症状在正常范围
    - range: [2, 2.99]
      level: 轻度
      description: 轻度强迫倾向，建议自我关注
    - range: [3, 3.99]
      level: 中度
      description: 中度强迫倾向，建议寻求专业咨询
    - range: [4, 4]
      level: 重度
      description: 重度强迫倾向，强烈建议精神科就诊
  interpersonal_sensitivity:
    - range: [0, 1.99]
      level: 正常
      description: 人际关系敏感在正常范围
    - range: [2, 2.99]
      level: 轻度
      description: 轻度人际关系敏感，建议自我关注
    - range: [3, 3.99]
      level: 中度
      description: 中度人际关系敏感，建议寻求专业咨询
    - range: [4, 4]
      level: 重度
      description: 重度人际关系敏感，强烈建议精神科就诊
  depression:
    - range: [0, 1.99]
      level: 正常
      description: 抑郁症状在正常范围
    - range: [2, 2.99]
      level: 轻度
      description: 轻度抑郁倾向，建议自我关注
    - range: [3, 3.99]
      level: 中度
      description: 中度抑郁倾向，建议寻求专业咨询
    - range: [4, 4]
      level: 重度
      description: 重度抑郁倾向，强烈建议精神科就诊
  anxiety:
    - range: [0, 1.99]
      level: 正常
      description: 焦虑症状在正常范围
    - range: [2, 2.99]
      level: 轻度
      description: 轻度焦虑倾向，建议自我关注
    - range: [3, 3.99]
      level: 中度
      description: 中度焦虑倾向，建议寻求专业咨询
    - range: [4, 4]
      level: 重度
      description: 重度焦虑倾向，强烈建议精神科就诊
  hostility:
    - range: [0, 1.99]
      level: 正常
      description: 敌对症状在正常范围
    - range: [2, 2.99]
      level: 轻度
      description: 轻度敌对倾向，建议自我关注
    - range: [3, 3.99]
      level: 中度
      description: 中度敌对倾向，建议寻求专业咨询
    - range: [4, 4]
      level: 重度
      description: 重度敌对倾向，强烈建议精神科就诊
  phobic_anxiety:
    - range: [0, 1.99]
      level: 正常
      description: 恐怖症状在正常范围
    - range: [2, 2.99]
      level: 轻度
      description: 轻度恐怖倾向，建议自我关注
    - range: [3, 3.99]
      level: 中度
      description: 中度恐怖倾向，建议寻求专业咨询
    - range: [4, 4]
      level: 重度
      description: 重度恐怖倾向，强烈建议精神科就诊
  paranoid_ideation:
    - range: [0, 1.99]
      level: 正常
      description: 偏执症状在正常范围
    - range: [2, 2.99]
      level: 轻度
      description: 轻度偏执倾向，建议自我关注
    - range: [3, 3.99]
      level: 中度
      description: 中度偏执倾向，建议寻求专业咨询
    - range: [4, 4]
      level: 重度
      description: 重度偏执倾向，强烈建议精神科就诊
  psychoticism:
    - range: [0, 1.99]
      level: 正常
      description: 精神病性症状在正常范围
    - range: [2, 2.99]
      level: 轻度
      description: 轻度精神病性倾向，建议自我关注
    - range: [3, 3.99]
      level: 中度
      description: 中度精神病性倾向，建议寻求专业咨询
    - range: [4, 4]
      level: 重度
      description: 重度精神病性倾向，强烈建议精神科就诊

additional_items: [19, 44, 59, 60, 64, 66, 89]   # 这些题目不计入任何因子，但仍计入总分
positive_item_threshold: 2                       # 单项得分≥2视为阳性项目
total_positive_threshold: 43                     # 阳性项目数>43提示阳性

---

## 题目

| 题号 | 题目内容 | 选项（分值=描述） | 反向计分 |
|------|----------|-------------------|----------|
| 1    | Headaches | 0=没有, 1=轻度, 2=中度, 3=相当重, 4=严重 | 否 |
| 2    | Nervousness or shakiness inside | 0=没有, 1=轻度, 2=中度, 3=相当重, 4=严重 | 否 |
| 3    | Unwanted thoughts, words, or ideas that won't leave your mind | 0=没有, 1=轻度, 2=中度, 3=相当重, 4=严重 | 否 |
| 4    | Faintness or dizziness | 0=没有, 1=轻度, 2=中度, 3=相当重, 4=严重 | 否 |
| 5    | Loss of sexual interest or pleasure | 0=没有, 1=轻度, 2=中度, 3=相当重, 4=严重 | 否 |
| 6    | Feeling critical of others | 0=没有, 1=轻度, 2=中度, 3=相当重, 4=严重 | 否 |
| 7    | The idea that someone else can control your thoughts | 0=没有, 1=轻度, 2=中度, 3=相当重, 4=严重 | 否 |
| 8    | Feeling others are to blame for most of your troubles | 0=没有, 1=轻度, 2=中度, 3=相当重, 4=严重 | 否 |
| 9    | Trouble remembering things | 0=没有, 1=轻度, 2=中度, 3=相当重, 4=严重 | 否 |
| 10   | Worried about sloppiness or carelessness | 0=没有, 1=轻度, 2=中度, 3=相当重, 4=严重 | 否 |
| 11   | Feeling easily annoyed or irritated | 0=没有, 1=轻度, 2=中度, 3=相当重, 4=严重 | 否 |
| 12   | Pains in heart or chest | 0=没有, 1=轻度, 2=中度, 3=相当重, 4=严重 | 否 |
| 13   | Feeling afraid in open spaces or on the streets | 0=没有, 1=轻度, 2=中度, 3=相当重, 4=严重 | 否 |
| 14   | Feeling low in energy or slowed down | 0=没有, 1=轻度, 2=中度, 3=相当重, 4=严重 | 否 |
| 15   | Thoughts of ending your life | 0=没有, 1=轻度, 2=中度, 3=相当重, 4=严重 | 否 |
| 16   | Hearing voices that other people do not hear | 0=没有, 1=轻度, 2=中度, 3=相当重, 4=严重 | 否 |
| 17   | Trembling | 0=没有, 1=轻度, 2=中度, 3=相当重, 4=严重 | 否 |
| 18   | Feeling that most people cannot be trusted | 0=没有, 1=轻度, 2=中度, 3=相当重, 4=严重 | 否 |
| 19   | Poor appetite | 0=没有, 1=轻度, 2=中度, 3=相当重, 4=严重 | 否 |
| 20   | Crying easily | 0=没有, 1=轻度, 2=中度, 3=相当重, 4=严重 | 否 |
| 21   | Feeling shy or uneasy with the opposite sex | 0=没有, 1=轻度, 2=中度, 3=相当重, 4=严重 | 否 |
| 22   | Feeling of being trapped or caught | 0=没有, 1=轻度, 2=中度, 3=相当重, 4=严重 | 否 |
| 23   | Suddenly scared for no reason | 0=没有, 1=轻度, 2=中度, 3=相当重, 4=严重 | 否 |
| 24   | Temper outbursts that you could not control | 0=没有, 1=轻度, 2=中度, 3=相当重, 4=严重 | 否 |
| 25   | Feeling afraid to go out of your house alone | 0=没有, 1=轻度, 2=中度, 3=相当重, 4=严重 | 否 |
| 26   | Blaming yourself for things | 0=没有, 1=轻度, 2=中度, 3=相当重, 4=严重 | 否 |
| 27   | Pains in lower back | 0=没有, 1=轻度, 2=中度, 3=相当重, 4=严重 | 否 |
| 28   | Feeling blocked in getting things done | 0=没有, 1=轻度, 2=中度, 3=相当重, 4=严重 | 否 |
| 29   | Feeling lonely | 0=没有, 1=轻度, 2=中度, 3=相当重, 4=严重 | 否 |
| 30   | Feeling blue | 0=没有, 1=轻度, 2=中度, 3=相当重, 4=严重 | 否 |
| 31   | Worrying too much about things | 0=没有, 1=轻度, 2=中度, 3=相当重, 4=严重 | 否 |
| 32   | Feeling no interest in things | 0=没有, 1=轻度, 2=中度, 3=相当重, 4=严重 | 否 |
| 33   | Feeling fearful | 0=没有, 1=轻度, 2=中度, 3=相当重, 4=严重 | 否 |
| 34   | Your feelings being easily hurt | 0=没有, 1=轻度, 2=中度, 3=相当重, 4=严重 | 否 |
| 35   | Other people being aware of your private thoughts | 0=没有, 1=轻度, 2=中度, 3=相当重, 4=严重 | 否 |
| 36   | Feeling others do not understand you or are unsympathetic | 0=没有, 1=轻度, 2=中度, 3=相当重, 4=严重 | 否 |
| 37   | Feeling that people are unfriendly or dislike you | 0=没有, 1=轻度, 2=中度, 3=相当重, 4=严重 | 否 |
| 38   | Having to do things very slowly to insure correctness | 0=没有, 1=轻度, 2=中度, 3=相当重, 4=严重 | 否 |
| 39   | Heart pounding or racing | 0=没有, 1=轻度, 2=中度, 3=相当重, 4=严重 | 否 |
| 40   | Nausea or upset stomach | 0=没有, 1=轻度, 2=中度, 3=相当重, 4=严重 | 否 |
| 41   | Feeling inferior to others | 0=没有, 1=轻度, 2=中度, 3=相当重, 4=严重 | 否 |
| 42   | Soreness of your muscles | 0=没有, 1=轻度, 2=中度, 3=相当重, 4=严重 | 否 |
| 43   | Feeling that you are watched or talked about by others | 0=没有, 1=轻度, 2=中度, 3=相当重, 4=严重 | 否 |
| 44   | Trouble falling asleep | 0=没有, 1=轻度, 2=中度, 3=相当重, 4=严重 | 否 |
| 45   | Having to check and double-check what you do | 0=没有, 1=轻度, 2=中度, 3=相当重, 4=严重 | 否 |
| 46   | Difficulty making decisions | 0=没有, 1=轻度, 2=中度, 3=相当重, 4=严重 | 否 |
| 47   | Feeling afraid to travel on buses, subways, trains | 0=没有, 1=轻度, 2=中度, 3=相当重, 4=严重 | 否 |
| 48   | Trouble getting your breath | 0=没有, 1=轻度, 2=中度, 3=相当重, 4=严重 | 否 |
| 49   | Hot or cold spells | 0=没有, 1=轻度, 2=中度, 3=相当重, 4=严重 | 否 |
| 50   | Having to avoid certain things, places, or activities because they frighten you | 0=没有, 1=轻度, 2=中度, 3=相当重, 4=严重 | 否 |
| 51   | Your mind going blank | 0=没有, 1=轻度, 2=中度, 3=相当重, 4=严重 | 否 |
| 52   | Numbness or tingling in parts of your body | 0=没有, 1=轻度, 2=中度, 3=相当重, 4=严重 | 否 |
| 53   | A lump in your throat | 0=没有, 1=轻度, 2=中度, 3=相当重, 4=严重 | 否 |
| 54   | Feeling hopeless about the future | 0=没有, 1=轻度, 2=中度, 3=相当重, 4=严重 | 否 |
| 55   | Trouble concentrating | 0=没有, 1=轻度, 2=中度, 3=相当重, 4=严重 | 否 |
| 56   | Feeling weak in parts of your body | 0=没有, 1=轻度, 2=中度, 3=相当重, 4=严重 | 否 |
| 57   | Feeling tense or keyed up | 0=没有, 1=轻度, 2=中度, 3=相当重, 4=严重 | 否 |
| 58   | Heavy feelings in your arms or legs | 0=没有, 1=轻度, 2=中度, 3=相当重, 4=严重 | 否 |
| 59   | Thoughts of death or dying | 0=没有, 1=轻度, 2=中度, 3=相当重, 4=严重 | 否 |
| 60   | Overeating | 0=没有, 1=轻度, 2=中度, 3=相当重, 4=严重 | 否 |
| 61   | Feeling uneasy when people are watching or talking about you | 0=没有, 1=轻度, 2=中度, 3=相当重, 4=严重 | 否 |
| 62   | Having thoughts that are not your own | 0=没有, 1=轻度, 2=中度, 3=相当重, 4=严重 | 否 |
| 63   | Having urges to beat, injure, or harm someone | 0=没有, 1=轻度, 2=中度, 3=相当重, 4=严重 | 否 |
| 64   | Awakening in the early morning | 0=没有, 1=轻度, 2=中度, 3=相当重, 4=严重 | 否 |
| 65   | Having to repeat the same actions such as touching, counting, washing | 0=没有, 1=轻度, 2=中度, 3=相当重, 4=严重 | 否 |
| 66   | Sleep that is restless or disturbed | 0=没有, 1=轻度, 2=中度, 3=相当重, 4=严重 | 否 |
| 67   | Having urges to break or smash things | 0=没有, 1=轻度, 2=中度, 3=相当重, 4=严重 | 否 |
| 68   | Having ideas or beliefs that others do not share | 0=没有, 1=轻度, 2=中度, 3=相当重, 4=严重 | 否 |
| 69   | Feeling very self-conscious with others | 0=没有, 1=轻度, 2=中度, 3=相当重, 4=严重 | 否 |
| 70   | Feeling uneasy in crowds, such as shopping or at a movie | 0=没有, 1=轻度, 2=中度, 3=相当重, 4=严重 | 否 |
| 71   | Feeling everything is an effort | 0=没有, 1=轻度, 2=中度, 3=相当重, 4=严重 | 否 |
| 72   | Spells of terror or panic | 0=没有, 1=轻度, 2=中度, 3=相当重, 4=严重 | 否 |
| 73   | Feeling uncomfortable about eating or drinking in public | 0=没有, 1=轻度, 2=中度, 3=相当重, 4=严重 | 否 |
| 74   | Getting into frequent arguments | 0=没有, 1=轻度, 2=中度, 3=相当重, 4=严重 | 否 |
| 75   | Feeling nervous when you are left alone | 0=没有, 1=轻度, 2=中度, 3=相当重, 4=严重 | 否 |
| 76   | Others not giving you proper credit for your achievements | 0=没有, 1=轻度, 2=中度, 3=相当重, 4=严重 | 否 |
| 77   | Feeling lonely even when you are with people | 0=没有, 1=轻度, 2=中度, 3=相当重, 4=严重 | 否 |
| 78   | Feeling so restless you couldn't sit still | 0=没有, 1=轻度, 2=中度, 3=相当重, 4=严重 | 否 |
| 79   | Feelings of worthlessness | 0=没有, 1=轻度, 2=中度, 3=相当重, 4=严重 | 否 |
| 80   | Feeling that familiar things are strange or unreal | 0=没有, 1=轻度, 2=中度, 3=相当重, 4=严重 | 否 |
| 81   | Shouting or throwing things | 0=没有, 1=轻度, 2=中度, 3=相当重, 4=严重 | 否 |
| 82   | Feeling afraid you will faint in public | 0=没有, 1=轻度, 2=中度, 3=相当重, 4=严重 | 否 |
| 83   | Feeling that people will take advantage of you if you let them | 0=没有, 1=轻度, 2=中度, 3=相当重, 4=严重 | 否 |
| 84   | Having thoughts about sex that bother you a lot | 0=没有, 1=轻度, 2=中度, 3=相当重, 4=严重 | 否 |
| 85   | The idea that you should be punished for your sins | 0=没有, 1=轻度, 2=中度, 3=相当重, 4=严重 | 否 |
| 86   | Feeling pushed to get things done | 0=没有, 1=轻度, 2=中度, 3=相当重, 4=严重 | 否 |
| 87   | The idea that something serious is wrong with your body | 0=没有, 1=轻度, 2=中度, 3=相当重, 4=严重 | 否 |
| 88   | Never feeling close to another person | 0=没有, 1=轻度, 2=中度, 3=相当重, 4=严重 | 否 |
| 89   | Feelings of guilt | 0=没有, 1=轻度, 2=中度, 3=相当重, 4=严重 | 否 |
| 90   | The idea that something is wrong with your mind | 0=没有, 1=轻度, 2=中度, 3=相当重, 4=严重 | 否 |