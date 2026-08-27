class SafetyChecker:
    """Detect real-time crisis signals in user messages.

    The questionnaire may already flag self-harm risk, but users can also
    express crisis during an ongoing conversation. This checker lets the agent
    switch to safety-first mode even when the initial profile has no risk flag.
    """

    CRISIS_KEYWORDS = (
        "自杀",
        "自残",
        "不想活",
        "想死",
        "结束生命",
        "伤害自己",
        "轻生",
        "活着没意思",
        "一了百了",
    )

    def check(self, text: str) -> bool:
        if not text:
            return False
        return any(keyword in text for keyword in self.CRISIS_KEYWORDS)
