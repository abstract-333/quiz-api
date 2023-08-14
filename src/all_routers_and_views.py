from api.admin_panel.admin_schemas import (
    UserAdmin,
    UniversityAdmin,
    SectionAdmin,
    RoleAdmin,
    QuestionAdmin,
    FeedbackAdmin,
    RatingAdmin,
    BlacklistAdmin,
    BlockedLevelAdmin,
    WarningAdmin
)
from api.auth.auth_router import auth_router
from api.feedback.feedback_router import feedback_router
from api.question.question_router import question_router
from api.quiz.quiz_router import quiz_router
from api.rating.rating_router import rating_router
from api.section.section_router import section_router
from api.university.university_router import university_router

all_routers = [
    auth_router,
    question_router,
    quiz_router,
    rating_router,
    feedback_router,
    section_router,
    university_router
]

all_admin_views = [
    UserAdmin,
    UniversityAdmin,
    SectionAdmin,
    RoleAdmin,
    QuestionAdmin,
    FeedbackAdmin,
    RatingAdmin,
    BlacklistAdmin,
    BlockedLevelAdmin,
    WarningAdmin
]
