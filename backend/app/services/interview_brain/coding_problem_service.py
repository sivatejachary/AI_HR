import uuid
import logging
from typing import Dict, Any, List, Optional
from sqlalchemy.orm import Session
from app.models.domain import CodingProblem
from app.services.interview_brain.experience_engine import ExperienceEngine

logger = logging.getLogger("coding_problem_service")

SEED_PROBLEMS = [
    # --- FRESHER (0 Yrs / College) ---
    {
        "id": "prob-fresher-dup-prevention",
        "title": "College Placement API Duplicate Submission Guard",
        "description": "You are building a campus placement portal API. Students submit their application details through an HTTP request. Sometimes a student double-clicks the 'Submit' button. Implement the core logic `prevent_duplicate_student_submission(submissions: List[Dict])` to detect and filter out duplicate submissions based on `student_id` while keeping the earliest timestamp.",
        "difficulty": "EASY",
        "language_options": ["python", "javascript", "java", "cpp", "go"],
        "input_format": "submissions: List[Dict[str, Any]] (containing student_id, timestamp, data)",
        "output_format": "List[Dict[str, Any]] containing deduplicated unique student applications",
        "examples": [
            {
                "input": "submissions = [{'student_id': 101, 'timestamp': 100}, {'student_id': 101, 'timestamp': 102}]",
                "output": "[{'student_id': 101, 'timestamp': 100}]",
                "explanation": "Second submission for student_id 101 is ignored."
            }
        ],
        "constraints": ["1 <= len(submissions) <= 10^3"],
        "expected_complexity": {"time": "O(N)", "space": "O(N)"},
        "reference_solution": "def prevent_duplicate_student_submission(submissions):\n    seen = set()\n    unique = []\n    for sub in sorted(submissions, key=lambda x: x['timestamp']):\n        sid = sub['student_id']\n        if sid not in seen:\n            seen.add(sid)\n            unique.append(sub)\n    return unique",
        "private_evaluation_notes": "Fresher scenario. Evaluate basic data structures (set/dict) vs quadratic nested loops.",
        "internal_scoring_rules": {"deduplication_logic": 0.5, "earliest_timestamp_preservation": 0.3, "time_complexity": 0.2}
    },

    # --- JUNIOR (0–2 Yrs) ---
    {
        "id": "prob-junior-request-validation",
        "title": "Employee API Request Validator & Error Sanitizer",
        "description": "Your HTTP API endpoint receives JSON payloads for creating employee records. Implement a validator `validate_employee_payload(payload: Dict)` that checks for required fields ('name', 'email', 'department'), validates email format containing '@' and '.', and returns a sanitized result `{'valid': bool, 'errors': List[str]}`.",
        "difficulty": "EASY",
        "language_options": ["python", "javascript", "java", "cpp", "go"],
        "input_format": "payload: Dict[str, Any]",
        "output_format": "Dict with boolean 'valid' flag and detailed error messages list",
        "examples": [
            {
                "input": "payload = {'name': 'Alice', 'email': 'invalid-email', 'department': 'Engineering'}",
                "output": "{'valid': False, 'errors': ['Invalid email format']}"
            }
        ],
        "constraints": ["Payload size <= 10KB"],
        "expected_complexity": {"time": "O(1)", "space": "O(1)"},
        "reference_solution": "def validate_employee_payload(payload):\n    errors = []\n    for field in ['name', 'email', 'department']:\n        if not payload.get(field):\n            errors.append(f'Missing required field: {field}')\n    email = payload.get('email', '')\n    if email and ('@' not in email or '.' not in email):\n        errors.append('Invalid email format')\n    return {'valid': len(errors) == 0, 'errors': errors}",
        "private_evaluation_notes": "Junior level. Check for clean error handling, boundary checks, and non-empty string validations.",
        "internal_scoring_rules": {"field_presence_check": 0.4, "email_validation": 0.3, "clean_error_formatting": 0.3}
    },

    # --- MID-LEVEL (2–5 Yrs) ---
    {
        "id": "prob-mid-double-booking-prevention",
        "title": "Concurrent Interview Slot Double-Booking Guard",
        "description": "In an interview scheduling system, two recruiters may attempt to book the exact same interviewer slot at almost the same millisecond. Implement `book_interview_slot(slot_id: str, recruiter_id: str, storage_state: Dict)` using an idempotent lock pattern to guarantee that only one booking succeeds, returning `{'success': bool, 'booked_by': str}`.",
        "difficulty": "MEDIUM",
        "language_options": ["python", "javascript", "java", "cpp", "go"],
        "input_format": "slot_id: str, recruiter_id: str, storage_state: Dict[str, Any]",
        "output_format": "Dict with booking status and confirmed recruiter",
        "examples": [
            {
                "input": "slot_id = 'slot-404', recruiter_id = 'rec-A', storage_state = {'slot-404': {'booked': False}}",
                "output": "{'success': True, 'booked_by': 'rec-A'}"
            }
        ],
        "constraints": ["Simulated concurrency under 1000 requests/sec"],
        "expected_complexity": {"time": "O(1)", "space": "O(1)"},
        "reference_solution": "def book_interview_slot(slot_id, recruiter_id, storage_state):\n    slot = storage_state.get(slot_id, {})\n    if slot.get('booked'):\n        return {'success': False, 'booked_by': slot.get('booked_by')}\n    slot['booked'] = True\n    slot['booked_by'] = recruiter_id\n    storage_state[slot_id] = slot\n    return {'success': True, 'booked_by': recruiter_id}",
        "private_evaluation_notes": "Mid-level concurrency problem. Ask candidate how they would translate local lock state into Redis lock / PostgreSQL SELECT FOR UPDATE in production.",
        "internal_scoring_rules": {"atomic_check_and_set": 0.4, "idempotency": 0.3, "concurrency_reasoning": 0.3}
    },

    # --- SENIOR (5–8 Yrs) ---
    {
        "id": "prob-senior-cache-stampede-mitigation",
        "title": "High-Throughput Candidate Search Cache Stampede Mitigation",
        "description": "Your candidate search API receives 50,000 requests/min. During peak traffic, when a hot Redis cache key expires, thousands of concurrent requests hit PostgreSQL directly, causing database CPU spikes and API latency to balloon from 300ms to 4s. Implement a probabilistic early expiration / mutext-locked cache fetcher `get_candidate_with_cache_guard(cache_key: str, fetch_from_db_fn, ttl: int)` that prevents cache stampedes.",
        "difficulty": "HARD",
        "language_options": ["python", "javascript", "java", "cpp", "go"],
        "input_format": "cache_key: str, fetch_from_db_fn: Callable, ttl: int",
        "output_format": "Dict containing candidate data with latency guarantee",
        "examples": [
            {
                "input": "cache_key = 'search-python-senior', ttl = 60",
                "output": "{'data': [...], 'source': 'CACHE_OR_MUTEX'}"
            }
        ],
        "constraints": ["50,000 req/min simulation scenario"],
        "expected_complexity": {"time": "O(1)", "space": "O(1)"},
        "reference_solution": "import time, threading\n_locks = {}\ndef get_candidate_with_cache_guard(cache_key, fetch_from_db_fn, ttl=60, cache_store={}):\n    cached = cache_store.get(cache_key)\n    now = time.time()\n    if cached and now < cached['expires_at']:\n        return {'data': cached['data'], 'source': 'CACHE'}\n    lock = _locks.setdefault(cache_key, threading.Lock())\n    if lock.acquire(blocking=False):\n        try:\n            data = fetch_from_db_fn()\n            cache_store[cache_key] = {'data': data, 'expires_at': time.time() + ttl}\n            return {'data': data, 'source': 'DB_FETCH'}\n        finally:\n            lock.release()\n    else:\n        return {'data': cached['data'] if cached else [], 'source': 'STALE_CACHE_FALLBACK'}",
        "private_evaluation_notes": "Senior production incident scenario. Evaluate mutex single-flight, XFetch probabilistic early expiration, and fallback grace period.",
        "internal_scoring_rules": {"single_flight_mutex": 0.4, "stale_cache_grace_fallback": 0.3, "production_metrics_reasoning": 0.3}
    },

    # --- STAFF (8+ Yrs) ---
    {
        "id": "prob-staff-multi-region-scheduler",
        "title": "Multi-Region Distributed Interview Scheduler Consistency Engine",
        "description": "Design and implement the core consistency validator `resolve_multi_region_schedule(region_events: List[Dict])` for an enterprise interview scheduling platform operating across 3 geographic regions (US-East, EU-West, AP-South). During a network partition event, events created in separate regions must be deterministically merged using vector clocks or fencing tokens to guarantee zero double bookings.",
        "difficulty": "EXPERT",
        "language_options": ["python", "javascript", "java", "cpp", "go"],
        "input_format": "region_events: List[Dict[str, Any]] (containing event_id, region, fencing_token, vector_clock, slot_id)",
        "output_format": "Dict containing deterministic schedule resolution, accepted events, and rejected conflicting events",
        "examples": [
            {
                "input": "region_events = [{'event_id': 'e1', 'region': 'US-East', 'fencing_token': 102, 'slot_id': 's1'}, {'event_id': 'e2', 'region': 'EU-West', 'fencing_token': 101, 'slot_id': 's1'}]",
                "output": "{'accepted': ['e1'], 'rejected': ['e2'], 'conflict_reason': 'Fencing token 102 supersedes 101'}"
            }
        ],
        "constraints": ["Multi-region partition recovery scenario"],
        "expected_complexity": {"time": "O(N log N)", "space": "O(N)"},
        "reference_solution": "def resolve_multi_region_schedule(region_events):\n    slots = {}\n    accepted, rejected = [], []\n    for evt in sorted(region_events, key=lambda x: (x['slot_id'], -x['fencing_token'])):\n        slot_id = evt['slot_id']\n        if slot_id not in slots:\n            slots[slot_id] = evt\n            accepted.append(evt['event_id'])\n        else:\n            rejected.append(evt['event_id'])\n    return {'accepted': accepted, 'rejected': rejected, 'resolution': 'Highest fencing token prioritized'}",
        "private_evaluation_notes": "Staff architecture level. Probe CAP theorem trade-offs, vector clocks vs Spanner TrueTime, and fencing tokens.",
        "internal_scoring_rules": {"fencing_token_resolution": 0.4, "partition_tolerance_reasoning": 0.3, "multi_region_failover": 0.3}
    }
]

class CodingProblemService:
    def __init__(self, db: Session):
        self.db = db

    def seed_initial_problems(self):
        """Ensures seed problems exist in DB."""
        for p in SEED_PROBLEMS:
            existing = self.db.query(CodingProblem).filter(CodingProblem.id == p["id"]).first()
            if not existing:
                prob = CodingProblem(
                    id=p["id"],
                    title=p["title"],
                    description=p["description"],
                    difficulty=p["difficulty"],
                    language_options=p["language_options"],
                    input_format=p["input_format"],
                    output_format=p["output_format"],
                    examples=p["examples"],
                    constraints=p["constraints"],
                    expected_complexity=p["expected_complexity"],
                    reference_solution=p["reference_solution"],
                    private_evaluation_notes=p["private_evaluation_notes"],
                    internal_scoring_rules=p["internal_scoring_rules"]
                )
                self.db.add(prob)
        self.db.commit()

    def select_problem(
        self,
        language: str = "python",
        difficulty: str = "MEDIUM",
        experience_band: str = "MID_LEVEL",
        role: Optional[str] = None
    ) -> CodingProblem:
        self.seed_initial_problems()
        
        # Map experience band to preferred problem difficulty/id
        band_map = {
            "FRESHER": "prob-fresher-dup-prevention",
            "JUNIOR": "prob-junior-request-validation",
            "MID_LEVEL": "prob-mid-double-booking-prevention",
            "SENIOR": "prob-senior-cache-stampede-mitigation",
            "STAFF": "prob-staff-multi-region-scheduler"
        }
        
        target_id = band_map.get(experience_band.upper(), "prob-mid-double-booking-prevention")
        prob = self.db.query(CodingProblem).filter(CodingProblem.id == target_id).first()
        
        if not prob:
            diff = (difficulty or "MEDIUM").upper()
            prob = self.db.query(CodingProblem).filter(CodingProblem.difficulty == diff).first()
        if not prob:
            prob = self.db.query(CodingProblem).first()
        return prob

    def get_public_problem_payload(self, problem: CodingProblem) -> Dict[str, Any]:
        """
        Returns ONLY public problem data for candidate API responses.
        STRICTLY excludes reference_solution, private_evaluation_notes, and internal_scoring_rules.
        """
        return {
            "id": problem.id,
            "title": problem.title,
            "description": problem.description,
            "difficulty": problem.difficulty,
            "language_options": problem.language_options or ["python", "javascript", "java"],
            "input_format": problem.input_format,
            "output_format": problem.output_format,
            "examples": problem.examples or [],
            "constraints": problem.constraints or [],
            "expected_complexity": problem.expected_complexity or {"time": "O(N)", "space": "O(N)"}
        }
