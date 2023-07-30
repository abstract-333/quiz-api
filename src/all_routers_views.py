from auth.auth_router import auth_router
from feedback.feedback_router import feedback_router
from question.question_router import question_router
from quiz.quiz_router import quiz_router
from rating.rating_router import rating_router
from section.section_router import section_router
from university.university_router import university_router
from admin.admin_schemas import UserAdmin, UniversityAdmin, SectionAdmin, RoleAdmin, \
    QuestionAdmin, FeedbackAdmin, RatingAdmin, BlacklistAdmin, BlockedLevelAdmin, WarningAdmin

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