from internal.service.user_service import UserService
from internal.service.society_service import SocietyService
from internal.service.feedback_service import FeedbackService
from internal.service.notice_service import NoticeService
from internal.service.invoice_service import InvoiceService


user_service_instance = UserService()
society_service_instance = SocietyService()
feedback_service_instance = FeedbackService()
notice_service_instance = NoticeService()
invoice_service_instance = InvoiceService()