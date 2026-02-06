"""Constants and enums for the Conversation Decision Framework"""
from enum import Enum, auto


class ConversationState(Enum):
    """
    The 7 conversation states for Buddy AI.

    Priority Order (for detection):
    1. OUT_OF_SCOPE - Safety first
    2. CONFUSED - Trust building
    3. VALIDATION_SEEKING - Trust building
    4. SELF_REFLECTION - Deepening awareness
    5. CAREER_CURIOSITY - Exploration
    6. COMPARISON - Exploration with trade-offs
    7. INFORMATION_SEEKING - Factual queries

    When multiple states seem possible, always choose the first match.
    Safety > Trust > Reflection > Exploration > Information
    """
    OUT_OF_SCOPE = auto()
    CONFUSED = auto()
    VALIDATION_SEEKING = auto()
    SELF_REFLECTION = auto()
    CAREER_CURIOSITY = auto()
    COMPARISON = auto()
    INFORMATION_SEEKING = auto()
    GREETING = auto()  # Special state for greetings


# Canonical out-of-scope response - MUST be used verbatim
CANONICAL_OUT_OF_SCOPE_RESPONSE = """I'm sorry — I don't have the right context to answer this.

I can help with careers, education, and future planning, but for this it would be better to speak with a trusted adult like a teacher or parent.

If you'd like, we can talk about your studies, career options, or future plans."""


# Out-of-scope topic patterns
OUT_OF_SCOPE_PATTERNS = {
    # Mental health related
    "mental_health": [
        "depressed", "depression", "anxiety", "anxious", "suicide",
        "self-harm", "self harm", "cutting", "kill myself", "want to die",
        "panic attack", "mental health", "therapy", "therapist",
        "stressed", "overwhelmed", "can't cope", "breaking down"
    ],

    # Relationships
    "relationships": [
        "boyfriend", "girlfriend", "dating", "crush", "love life",
        "breakup", "broke up", "relationship advice", "ex-", "my ex",
        "cheating", "cheated"
    ],

    # Family conflict
    "family": [
        "parents fighting", "divorce", "family problems", "abuse",
        "hitting me", "beats me", "scared of my parents"
    ],

    # Politics/Religion
    "politics_religion": [
        "politics", "political", "election", "vote", "government",
        "religion", "religious", "god", "pray", "muslim", "hindu",
        "christian", "caste", "reservation"
    ],

    # Explicit content
    "explicit": [
        "sex", "porn", "naked", "nude"
    ],

    # Violence
    "violence": [
        "fight", "violence", "weapon", "gun", "knife", "hurt someone"
    ]
}

# Confusion signal patterns
CONFUSION_PATTERNS = [
    "i don't know", "i dont know", "idk",
    "i'm confused", "im confused", "confused",
    "i have no idea", "no idea",
    "i'm lost", "im lost", "lost",
    "what should i do", "help me",
    "i'm not sure", "im not sure", "not sure",
    "don't understand", "dont understand",
    "everything is confusing", "so confused",
    "no clue", "clueless"
]

# Validation seeking patterns
VALIDATION_PATTERNS = [
    "am i good enough", "can i become", "will i be able to",
    "is it bad if", "is it okay if", "is it wrong",
    "should i", "do you think i can",
    "am i smart enough", "am i capable",
    "is it too late", "is it possible for me",
    "can someone like me", "people like me",
    "am i making a mistake", "is this a bad choice"
]

# Self-reflection patterns
SELF_REFLECTION_PATTERNS = [
    "i like", "i love", "i enjoy",
    "i hate", "i don't like", "i dislike",
    "i'm good at", "im good at", "i am good at",
    "i'm bad at", "im bad at", "i am bad at",
    "i prefer", "i find", "i feel",
    "interests me", "bores me",
    "i want to", "i wish", "i hope"
]

# Career curiosity patterns
CAREER_PATTERNS = [
    "what does a", "what do", "tell me about",
    "how to become", "how do i become",
    "what is it like to be", "what's it like",
    "career in", "job as", "work as",
    "day in the life", "typical day"
]

# Comparison patterns
COMPARISON_PATTERNS = [
    " vs ", " versus ", " or ",
    "which is better", "what's better", "whats better",
    "difference between", "compare",
    "should i choose", "science or commerce",
    "engineering or", "doctor or", "better option"
]

# Information seeking patterns
INFORMATION_PATTERNS = [
    "how much", "salary", "pay", "income", "earn",
    "entrance exam", "exam", "jee", "neet", "cat", "clat",
    "college", "university", "iit", "nit", "aiims",
    "fee", "fees", "cost", "tuition",
    "eligibility", "qualification", "degree", "required",
    "years", "duration", "how long"
]

# Greeting patterns
GREETING_PATTERNS = [
    "hi", "hello", "hey", "hii", "hiii",
    "sup", "yo", "hola", "namaste",
    "good morning", "good afternoon", "good evening",
    "what's up", "whats up", "howdy"
]

# State-specific response guidelines
STATE_GUIDELINES = {
    ConversationState.CONFUSED: {
        "goal": "Reduce pressure",
        "do": [
            "Normalize confusion",
            "Ask ONE very easy question",
            "Be warm and supportive"
        ],
        "dont": [
            "List careers",
            "Give advice",
            "Overwhelm with options"
        ],
        "max_questions": 1
    },

    ConversationState.VALIDATION_SEEKING: {
        "goal": "Remove judgment",
        "do": [
            "Reframe away from ability",
            "Redirect to exploration",
            "Be encouraging without making promises"
        ],
        "dont": [
            "Say yes or no directly",
            "Predict success or failure",
            "Give false assurance"
        ],
        "max_questions": 1
    },

    ConversationState.SELF_REFLECTION: {
        "goal": "Deepen awareness and trust",
        "do": [
            "Acknowledge the insight",
            "Reflect it back",
            "Ask one gentle follow-up",
            "Store as memory"
        ],
        "dont": [
            "Label the student",
            "Jump to careers immediately",
            "Make assumptions"
        ],
        "max_questions": 1
    },

    ConversationState.CAREER_CURIOSITY: {
        "goal": "Provide realistic exposure",
        "do": [
            "Explain day-to-day work",
            "Describe what it feels like",
            "End with a reflection question"
        ],
        "dont": [
            "Hype prestige or status",
            "Start with salary",
            "Make it sound better than it is"
        ],
        "max_questions": 1
    },

    ConversationState.COMPARISON: {
        "goal": "Explain trade-offs",
        "do": [
            "Compare nature of work",
            "Stay neutral",
            "Ask preference-based question"
        ],
        "dont": [
            "Rank options",
            "Recommend one over other",
            "Be biased"
        ],
        "max_questions": 1
    },

    ConversationState.INFORMATION_SEEKING: {
        "goal": "Provide clarity without overload",
        "do": [
            "Give basic facts",
            "Keep concise",
            "Offer to go deeper if interested"
        ],
        "dont": [
            "Dump long lists",
            "Push decisions",
            "Overwhelm with data"
        ],
        "max_questions": 1
    },

    ConversationState.OUT_OF_SCOPE: {
        "goal": "Set boundary without breaking trust",
        "do": [
            "Acknowledge",
            "Redirect gently",
            "Leave door open for career talk"
        ],
        "dont": [
            "Scold",
            "Explain policy",
            "Continue the topic"
        ],
        "max_questions": 0
    },

    ConversationState.GREETING: {
        "goal": "Build warmth and trust",
        "do": [
            "Respond warmly",
            "Introduce yourself briefly",
            "Invite conversation"
        ],
        "dont": [
            "Be too formal",
            "Give long introductions",
            "Ask too many questions"
        ],
        "max_questions": 1
    }
}
