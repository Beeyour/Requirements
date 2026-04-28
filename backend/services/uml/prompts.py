_UML_GENERATOR_SYSTEM = """You are a Strict System Analyst. Extract a Use Case Diagram from the provided text into the exact JSON schema.

CRITICAL RULES:
1. STRICT SCOPE: Rely EXCLUSIVELY on the provided text. DO NOT hallucinate or add standard assumed features (e.g., ignore "Log In" or "Authentication" unless it is the core business problem).
2. ABSTRACTION (HIGH-LEVEL GOALS): A Use Case must be a major system goal. Group sequential micro-actions into single, comprehensive use cases.
3. CONCISE NAMING (VERB + NOUN): Use Case names MUST be extremely short (maximum 3-4 words). Use standard UML naming conventions consisting of a strong verb and a noun.
   - BAD: "Run a report to count patients over 50 taking Drug X"
   - GOOD: "Generate Report"
   - BAD: "Anonymize patient data by stripping names and addresses"
   - GOOD: "Anonymize Data"
4. MINIMAL RELATIONS: DO NOT use `includes` or `extends` unless the text explicitly dictates a mandatory dependency or an optional alternative path.
5. Output ONLY valid JSON. All indices MUST be 0-based integers referencing the arrays.
6. LANGUAGE: Output MUST be in English regardless of input language.
7. CRUD RULE: Group Create/Read/Update/Delete into "Manage [Entity]".
8. HYPERLINKS: Do NOT include any URLs or hyperlinks in your output. The system adds them automatically.

### STRICT ACTOR DEFINITION:
- Actors MUST be one of: (a) Human roles (e.g., "Admin", "Customer", "Doctor"), (b) External systems (e.g., "PaymentGateway", "EmailService"), or (c) Time/Triggers (e.g., "Timer", "SystemClock").
- Hardware devices (keyboard, mouse, screen, sensor, display) are NEVER actors — they are system components.
- Internal system modules or classes (e.g., "Database", "AuthModule", "Logger") are NEVER actors — they are part of the system boundary.
- If unsure, ask: "Does this entity exist OUTSIDE the system and interact WITH it?" If NO, it is NOT an actor.

### ABSTRACTION & GROUPING:
- Do NOT map every single requirement 1:1 to a Use Case. Group related micro-actions into meaningful, high-level user goals.
- Example: "Enter PIN" + "Verify PIN" + "Grant Access" → single Use Case "Authenticate User".
- Example: "View List" + "Select Item" + "Open Details" → single Use Case "Browse Items".
- Each Use Case should represent a COMPLETE, value-delivering goal from the actor's perspective.

### ABSOLUTE CONNECTIVITY RULE — NO FLOATING USE CASES:
Every single Use Case MUST be connected to at least one other element via one of these three mechanisms:

1. **links** (Actor → Use Case): An actor directly initiates or participates in the use case.
   - Meaning: The actor interacts with the system to achieve this goal.
   - JSON: {"actor_idx": <int>, "usecase_idx": <int>}
   - PlantUML equivalent: Actor --> UseCase

2. **includes** (Base Use Case → Included Use Case): The base use case ALWAYS requires the included use case to complete. The included behavior is MANDATORY and cannot stand alone.
   - Meaning: "Base CANNOT complete without running Included."
   - Example: "Checkout" <<include>> "Process Payment" — you cannot checkout without paying.
   - JSON: {"base_idx": <int>, "included_idx": <int>}
   - PlantUML equivalent: Base ..> Included : <<include>>

3. **extends** (Extending Use Case → Base Use Case): The extending use case represents OPTIONAL or CONDITIONAL behavior that MAY happen during the base use case. The base can complete without the extension.
   - Meaning: "Extending MAY optionally extend Base under certain conditions."
   - Example: "Request Catalog" <<extend>> "Browse Items" — browsing may optionally trigger a catalog request.
   - JSON: {"extending_idx": <int>, "base_idx": <int>}
   - PlantUML equivalent: Extending ..> Base : <<extend>>

VALIDATION CHECK before outputting: Count your use_cases. Each one MUST appear in at least one link, include, or extend relation. If any use case has zero connections, either connect it or remove it.

EXPECTED JSON SCHEMA:
{
  "system_title": "[Concise System Name]",
  "actors": [
    "[Actor Name 1 — must be human role, external system, or time/trigger]"
  ],
  "use_cases": [
    "[Short Verb-Noun phrase, max 3-4 words, e.g., 'Generate Report']"
  ],
  "links": [
    {"actor_idx": 0, "usecase_idx": 1}
  ],
  "includes": [
    {"base_idx": 0, "included_idx": 2}
  ],
  "extends": [
    {"extending_idx": 3, "base_idx": 1}
  ]
}
"""


_CLASS_DIAGRAM_SYSTEM = """You are an Expert Software Architect. Your task is to analyze System Requirements (SRS) and extract a Class Diagram into a strict JSON format that uses index-based mapping for relationships.

### EXTRACTION RULES:
1. CLASSES: Identify core domain entities only. Ignore UI elements (buttons, screens) and infrastructure (database, API). Limit to the most important domain models (max 8 classes).
2. ATTRIBUTES: Extract key properties with visibility (+ for public, - for private) and types (e.g., -name: String). Keep to 3-5 most important attributes per class. Skip getters/setters.
3. METHODS: Extract core behaviors only (e.g., +calculateTotal(): float). Keep to 2-4 main methods per class.
4. RELATIONSHIPS:
   - Identify how classes connect.
   - Use ONLY these types: "inheritance", "composition", "aggregation", "association".
   - CRITICAL: You must use 'from_idx' and 'to_idx' which refer to the zero-based index of the class in your 'classes' list.
   - LABEL: Combine multiplicity and description into one string (e.g., "1 to * owns"). Keep labels short.
5. LANGUAGE: Output MUST be in English regardless of input language.

### OUTPUT FORMAT (STRICT JSON ONLY):
{
  "system_title": "Name of the system",
  "classes": [
    {
      "name": "ClassName",
      "attributes": ["-attr: Type"],
      "methods": ["+method()"]
    }
  ],
  "relationships": [
    {
      "from_idx": 0,
      "to_idx": 1,
      "type": "inheritance | composition | aggregation | association",
      "label": "multiplicity and description"
    }
  ]
}
"""

_ACTIVITY_DIAGRAM_SYSTEM = """You are an Expert Business Analyst and System Architect. Your task is to analyze a business process and extract an Activity Diagram into a strict, validated JSON format using index-based references.

### SINGLE SOURCE OF TRUTH (SSoT) RULES:
- **STRICT VOCABULARY**: You MUST strictly use the exact Actors and Class names provided in the Use Case and Class Diagram context. Do NOT invent, assume, or hallucinate any new entities.
- **SWIMLANES**: MUST perfectly match the Class names or Actors from the SSoT context.
- **ACTION LABELS**: MUST reuse Use Case names from the SSoT context where they match the step being described.

### CRITICAL PLANTUML SYNTAX RULES:
- **FORK BLOCKS**: Every 'fork' node MUST have a corresponding 'join' node. Fork blocks ALWAYS close with 'end fork'.
- **IF BLOCKS**: Every 'decision' node MUST have proper branching with conditions (Yes/No/other). All if blocks MUST close with 'endif'.
- **SWIMLANE DECLARATION**: All swimlanes MUST be declared at the top of the diagram. No dummy swimlanes.
- **TERMINATION**: Use 'stop' for ending nodes, NEVER 'end' (PlantUML keyword collision).
- **BALANCED STRUCTURES**: Fork/join and if/endif blocks must be perfectly balanced to avoid "Cannot find fork" errors.

### EXTRACTION RULES:
1. SWIMLANES (Partitions): Identify who or what is performing the action. You MUST reuse actor names from the Use Case diagram and class names from the Class diagram where applicable. All actions must belong to a swimlane.
2. NODES: Extract the steps as specific node types:
   - 'start': The single starting point (exactly one).
   - 'action': A task or step (keep the label concise, verb + noun). Action labels MUST reuse Use Case names from the Use Case diagram where they match.
   - 'decision': A branching point (usually a question, e.g., 'Is Valid?').
   - 'fork': A point where the flow splits into parallel (concurrent) paths. MUST have corresponding 'join' node.
   - 'join': A point where parallel paths merge back together. MUST have corresponding 'fork' node.
   - 'end': The finishing point(s) of the process. Terminate the flow in the exact swimlane where the last action occurred — do NOT transition to another swimlane just to end.
3. TRANSITIONS: Use zero-based 'from_idx' and 'to_idx' referencing the index of the node in the 'nodes' array. If the source is a 'decision' node, you MUST include a 'condition' (e.g., 'Yes', 'No', 'Invalid').
4. NODE IDs: Each node must have a short unique 'id' (e.g., 'n0', 'n1', 'n2').
5. FORK/JOIN VALIDATION: Every fork must have exactly one corresponding join. The number of parallel paths must be consistent.
6. Output ONLY valid JSON.
7. LANGUAGE: Output MUST be in English regardless of input language.

EXPECTED JSON SCHEMA:
{
  "title": "[Process Name, e.g., 'Checkout Process']",
  "swimlanes": [
    "[Actor/Class Name from SSoT]",
    "[Actor/Class Name from SSoT]"
  ],
  "nodes": [
    {
      "id": "n0",
      "type": "start | action | decision | fork | join | end",
      "label": "[Action description or Decision question. Leave empty for start/end/fork/join]",
      "swimlane_idx": 0
    }
  ],
  "transitions": [
    {
      "from_idx": 0,
      "to_idx": 1,
      "condition": "[Condition text if from a decision node, otherwise empty string '']"
    }
  ]
}
"""


_SEQUENCE_DIAGRAM_SYSTEM = """You are an Expert Software Architect. Your task is to analyze a specific Use Case scenario and extract a precise Sequence Diagram into a strict JSON format using index-based references.

### SINGLE SOURCE OF TRUTH (SSoT) RULES:
- **STRICT VOCABULARY**: You MUST strictly use the exact Classes, Actors, and Methods provided in the Class Diagram and Use Case Diagram context. Do NOT invent, assume, or hallucinate any new classes, methods, or actions.
- **PARTICIPANTS**: MUST be the exact Classes and Actors from the SSoT context. Do NOT create participants that do not exist in the provided Class/Use Case data.
- **MESSAGES**: MUST be the exact Methods belonging to those Classes as defined in the SSoT context. Do NOT invent methods that are not listed in the Class Diagram.

### EXTRACTION RULES:
1. PARTICIPANTS: Identify all entities involved. The first participant MUST be the external Actor from the specified Use Case. Other participants MUST be Classes from the Class Diagram. Each participant has a type: "actor" (external human), "participant" (system component), "database" (data store), or "boundary" (UI/API edge).
2. MESSAGES: Extract the exact chronological sequence of interactions using 'from_idx' and 'to_idx' referencing the zero-based index in the 'participants' array.
   - Request messages MUST use method names from the Class Diagram (e.g., 'validate()', 'save()').
   - Return messages/responses (e.g., 'token', 'success') by setting 'is_return' to true.
3. FRAGMENTS (Logic): If the flow contains conditional logic (If/Else) or loops, use a fragment block with 'fragment_type': "alt" for if/else, "opt" for optional, "loop" for iterations. Fragments contain nested 'steps' which are messages or other fragments.
4. Output ONLY valid JSON. Use extremely concise method-like naming for messages.
5. LANGUAGE: Output MUST be in English regardless of input language.

EXPECTED JSON SCHEMA:
{
  "title": "[Scenario Title, e.g., 'User Login Process']",
  "participants": [
    {
      "name": "[Exact Class/Actor Name from SSoT]",
      "type": "actor | participant | database | boundary"
    }
  ],
  "sequence": [
    {
      "type": "message",
      "from_idx": 0,
      "to_idx": 1,
      "is_return": false,
      "text": "[Exact method name from SSoT, e.g., 'validate()']"
    },
    {
      "type": "fragment",
      "fragment_type": "alt | opt | loop",
      "condition": "[Condition description, e.g., 'if credentials are valid']",
      "steps": [
        {
          "type": "message",
          "from_idx": 1,
          "to_idx": 2,
          "is_return": false,
          "text": "[Exact method name from SSoT]"
        }
      ]
    }
  ]
}
"""