from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.conf import settings
import logging

logger = logging.getLogger(__name__)


class MailService:

    @staticmethod
    def send_email(subject: str, template: str, context: dict, recipient_list: list):
        """
        Méthode générique pour envoyer un email HTML + texte
        """
        try:
            html_content = render_to_string(template, context)
            text_content = strip_tags(html_content)

            email = EmailMultiAlternatives(
                subject=subject,
                body=text_content,
                from_email=settings.DEFAULT_FROM_EMAIL,
                to=recipient_list,
            )

            email.attach_alternative(html_content, "text/html")
            email.send()

            logger.info(f"Email envoyé à {recipient_list}")

        except Exception as e:
            logger.error(f"Erreur envoi email : {e}")

     # ==============================
    # 👤 Confirmation inscription
    # ==============================
    @staticmethod
    def send_registration_confirmation(user):
        MailService.send_email(
            subject="Bienvenue sur Lausa Fashion 🎉",
            template="emails/confirmation_inscription.html",
            context={"user": user},
            recipient_list=[user.email],
        )

    """
    # ==============================
    # 📦 Confirmation commande
    # ==============================
    @staticmethod
    def send_order_confirmation(commande):
        MailService.send_email(
            subject="Confirmation de votre commande",
            template="emails/confirmation_commande.html",
            context={
                "commande": commande,
                "client": commande.client,
            },
            recipient_list=[commande.client.email],
        )
   
    # ==============================
    # 🚚 Notification livraison
    # ==============================
    @staticmethod
    def send_delivery_notification(livraison):
        MailService.send_email(
            subject="Votre commande est en route 🚚",
            template="emails/notification_livraison.html",
            context={"livraison": livraison},
            recipient_list=[livraison.commande.client.email],
        )

    # ==============================
    # 🔐 Email OTP
    # ==============================
    @staticmethod
    def send_otp_email(user, otp_code):
        MailService.send_email(
            subject="Code de vérification",
            template="emails/otp_verification.html",
            context={
                "user": user,
                "otp_code": otp_code,
            },
            recipient_list=[user.email],
        )
    """