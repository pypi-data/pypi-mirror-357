"""
Template Variables Registry

This module provides a registry of template variables for different template types.
Each template type has its own set of required and optional variables with example values.
"""

from typing import Dict, Any, TypedDict, Optional
from typing_extensions import NotRequired


class TemplateVariables(TypedDict, total=False):
    """Base class for template variables with common fields."""

    website_url: NotRequired[str]


class CalendarAppPromoVars(TemplateVariables):
    """Variables for calendar app promotion template."""

    cta_text: str
    image_url: str
    cta_image: str
    heading: str
    subheading: str
    contact_email: str
    contact_phone: str
    quote: str
    user_avatar: str
    user_name: str
    user_title: str
    testimonial_text: str


class TestimonialVars(TemplateVariables):
    """Variables for testimonial template."""

    user_avatar: str
    user_name: str
    user_title: str
    testimonial_text: str


class BlogPostVars(TemplateVariables):
    """Variables for blog post template."""

    title: str
    author: str
    read_time: str
    image_url: str


class QATemplateVars(TemplateVariables):
    """Variables for Q&A template."""

    question: str
    answer: str
    username: str


class QuoteTemplateVars(TemplateVariables):
    """Variables for quote template."""

    quote1: str
    quote2: str
    username: str


class EducationInfoVars(TemplateVariables):
    """Variables for education info template."""

    testimonial_text: str
    author: str
    read_time: str
    image_url: str


class ProductPromotionVars(TemplateVariables):
    """Variables for product promotion template."""

    image_url: str
    quote1: str
    quote2: str


class ProductShowcaseVars(TemplateVariables):
    """Variables for product showcase template."""

    product_image: str
    product_name: str
    product_price: str
    product_description: str
    badge_text: str


# Registry mapping template names to their variable types and example values
TEMPLATE_VARIABLES_REGISTRY: Dict[str, Dict[str, Any]] = {
    "default": {
        "type": "default",
        "description": "Default template",
        "variables": {
            "cta_text": "LEARN MORE",
            "logo_url": "https://img.freepik.com/free-vector/bird-colorful-logo-gradient-vector_343694-1365.jpg",
            "image_url": "Generate a prompt for a vibrant image of this tool to be featured on isntagram",
            "cta_image": "https://images.unsplash.com/photo-1556742049-0cfed4f6a45d",
            "heading": "plan your day in a snap",
            "subheading": "Driving success",
            "contact_email": "contact@business.com",
            "contact_phone": "+1-800-555-1234",
            "website_url": "dolze.ai /download",
            "quote": "The only way to do great work is to love what you do.",
            "theme_color": "#44EC9D",
            "user_avatar": "https://img.freepik.com/free-vector/blue-circle-with-white-user_78370-4707.jpg?ga=GA1.1.1623013982.1744968336&semt=ais_hybrid&w=740",
            "user_name": "Alex Johnson",
            "user_title": "Marketing Director, TechCorp",
            "testimonial_text": "This product has completely transformed how we works. The intuitive interface and powerful features have saved us countless hours.",
            "caption": "Create a caption: Highlight the ease of boosting productivity with an intuitive tool for planning and tracking tasks, under 300 characters, with hashtags",
        },
        "required": ["caption"],
    },
    "calendar_app_promo": {
        "type": "promotional",
        "description": "Calendar app promotion template",
        "variables": {
            "image_url": "Generate a prompt for a sleek image of a calendar app interface with a modern, minimalist design, showing a monthly view with colorful events, on a smartphone screen",
            "heading": "Plan your day in a snap",
            "caption": "Create a caption: Promote a calendar app for seamless scheduling and organization, under 300 characters, with hashtags",
        },
        "required": ["cta_text", "image_url", "heading", "subheading"],
    },
    "testimonials_template": {
        "type": "testimonial",
        "description": "Customer testimonial template",
        "variables": {
            "user_avatar": "https://example.com/avatar.jpg",
            "user_name": "Sarah Johnson",
            "user_title": "Verified Buyer",
            "testimonial_text": "This product has transformed how we work.",
            "caption": "Create a caption: Showcase a customer testimonial highlighting workflow transformation, under 300 characters, with hashtags",
        },
        "required": ["user_name", "testimonial_text"],
    },
    "blog_post": {
        "type": "blog",
        "description": "Blog post template with featured image",
        "variables": {
            "title": "How to be environment conscious without being weird",
            "author": "@username",
            "read_time": "4",
            "image_url": "Generate a prompt for an image of an eco-friendly scene with sustainable practices like recycling, solar panels, and greenery, in a bright, inviting style",
            "website_url": "example.com",
            "logo_url": "https://img.freepik.com/free-vector/bird-colorful-logo-gradient-vector_343694-1365.jpg",
            "publish_date": "2025-06-22",
            "excerpt": "This is a short description of the blog post. This will be used to display the blog post in the feed.",
            "caption": "Create a caption: Summarize eco-conscious lifestyle tips that are practical, under 300 characters, with hashtags",
        },
        "required": [
            "title",
            "author",
            "read_time",
            "image_url",
            "website_url",
            "logo_url",
        ],
    },
    "blog_post_2": {
        "type": "blog",
        "description": "Blog post template with featured image",
        "variables": {
            "title": "How to be environment conscious without being weird",
            "author": "@username",
            "read_time": "4",
            "image_url": "Generate a prompt for a vibrant image of green living practices, featuring reusable items, plants, and a modern eco-home, in a clean, aesthetic style",
            "publish_date": "2025-06-22",
            "excerpt": "This si a short description of the blog post. this is to be inserted by db and will be used to display the blog post in the feed",
            "caption": "Create a caption: Promote simple, practical green living tips, under 300 characters, with hashtags",
        },
        "required": ["title", "author", "read_time", "image_url"],
    },
    "qa_template": {
        "type": "qna",
        "description": "Question and answer template",
        "variables": {
            "question": "A question in under 3-4 words",
            "answer": "One wind turbine can produce enough electricity to power around 1,500 homes annually!",
            "username": "@username",
            "caption": "Create a caption: Highlight wind energy facts from a Q&A, focusing on turbine power, under 300 characters, with hashtags",
        },
        "required": ["question", "answer", "username"],
    },
    "qa_template_2": {
        "type": "qna",
        "description": "Question and answer template",
        "variables": {
            "question": "a question in under 3-4 words",
            "answer": "a 30-40 words answer for the above question",
            "username": "@username",
            "caption": "Create a caption: Share wind turbine energy insights from a Q&A, under 300 characters, with hashtags ",
        },
        "required": ["question", "answer", "username"],
    },
    "qa_template_3": {
        "type": "qna",
        "description": "Question and answer template",
        "variables": {
            "question": "a question about the product/product space in which it operates in under 3-4 words",
            "answer": "a 24-30 words answer for the above question",
            "username": "@username",
            "caption": "Create a caption: Promote wind energy knowledge from a Q&A session, under 300 characters, with hashtags",
        },
        "required": ["question", "answer", "username"],
    },
    "quote_template": {
        "type": "quote",
        "description": "Inspirational quote template",
        "variables": {
            "quote1": "The only way to do",
            "quote2": "great work is to love what you do",
            "username": "@stevejobs",
            "caption": "Create a caption: Share an inspiring Steve Jobs quote about passion and work, under 300 characters, with hashtags",
        },
        "required": ["quote1", "quote2", "username"],
    },
    "quote_template_2": {
        "type": "quote",
        "description": "Inspirational quote template",
        "variables": {
            "quote1": "genereate a phrase in about 35-40 words about this business/problem its solving or the industry it operates in",
            "username": "@stevejobs",
            "caption": "Create a caption: Highlight Steve Jobs' wisdom on passion-driven work, under 300 characters, with hashtags ",
        },
        "required": ["quote1", "quote2", "username"],
    },
    "education_info": {
        "type": "education",
        "description": "Educational information template",
        "variables": {
            "product_info": "Write a brief text in under 600 chars which is a fact related to company or domain they operate in",
            "product_name": "Product Name",
            "author": "@username",
            "read_time": "4",
            "image_url": "Generate a prompt for an image of a wind turbine in a scenic landscape with clear skies and rolling hills, in a realistic style",
            "caption": "Create a caption: Educate about wind turbine energy output, under 300 characters, with hashtags",
        },
        "required": ["testimonial_text", "author", "read_time", "image_url"],
    },
    "education_info_2": {
        "type": "education",
        "description": "Educational information template",
        "variables": {
            "product_info": "a faq regarding the product or company or the domain they operate in, in under 300 chars",
            "author": "@username",
            "read_time": "4",
            "image_url": "Generate a prompt for an image of a clean energy scene with multiple wind turbines in a modern, eco-friendly landscape",
            "caption": "Create a caption: Share the community impact of wind energy, under 300 characters, with hashtags",
        },
        "required": ["testimonial_text", "author", "read_time", "image_url"],
    },
    "product_promotion": {
        "type": "promotional",
        "description": "Product promotion template",
        "variables": {
            "image_url": "Generate a prompt for a visually appealing portrait image of the product. The image should be in a clean, modern style and in portrait format",
            "heading": "a simple 2-3 word heading related to the product",
            "subheading": "a simple 30-40 word subheading related to the product",
            "cta_text": "a simple 1-2 word CTA text related to the product",
            "caption": "Create a caption: Promote a kanban board for effortless task organization, under 300 characters, with hashtags",
            "website_url": "a simple 1-2 word website url related to the product",
        },
        "required": [
            "image_url",
            "heading",
            "subheading",
            "logo_url",
            "cta_text",
            "website_url",
        ],
    },
    "product_promotion_2": {
        "type": "promotional",
        "description": "Product promotion template",
        "variables": {
            "image_url": "Generate a prompt for a visually appealing image of a kanban board interface with colorful task cards and a modern, user-friendly layout",
            "quote1": "the first line of quote in 3-4 words to be shown in white color",
            "quote2": "the continued quote to be shown in next line for few words",
            "caption": "Create a caption: Promote a kanban board for effortless task organization, under 300 characters, with hashtags",
        },
        "required": ["image_url", "quote1", "quote2"],
    },
    "product_showcase": {
        "type": "product",
        "description": "Product showcase template",
        "variables": {
            "product_image": "Generate a prompt for a high-quality image for this product based on context you have",
            "product_name": "Product Name",
            "product_price": "a price for this product in INR",
            "product_description": "crisp and brief product description in under 100 chars ",
            "badge_text": "Bestseller",
            "caption": "Create a caption: Showcase a bestselling premium product priced at $99.99, under 300 characters, with hashtags",
        },
        "required": ["product_image", "product_name", "product_price"],
    },
    "product_showcase_2": {
        "type": "product",
        "description": "Product showcase template",
        "variables": {
            "product_image": "Generate a prompt for a high-quality image for this product based on context you have",
            "product_name": "Product Name",
            "product_price": "a price for this product in INR",
            "product_description": "Detailed product description in aroudn 18-21 words",
            "badge_text": "Bestseller, Dont change it keep it bestseller always",
            "caption": "Create a caption: Highlight a top-rated product for $99.99, under 300 characters, with hashtags",
        },
        "required": ["product_image", "product_name", "product_price"],
    },
    "product_showcase_3": {
        "type": "product",
        "description": "Product showcase template",
        "variables": {
            "product_image": "Generate a prompt for a high-quality image for this product based on context you have",
            "product_name": "Product Name",
            "product_price": "$99.99",
            "product_description": "Detailed product description",
            "badge_text": "Bestseller",
            "caption": "Create a caption: Promote a bestselling product for $99.99, under 300 characters, with hashtags",
        },
        "required": ["product_image", "product_name", "product_price"],
    },
    "promotional_banner": {
        "type": "promotional",
        "description": "Promotional banner template",
        "variables": {
            "image_url": "Generate a prompt for a visually appealing image of this product",
            "heading": "Heading in under 3 words",
            "subheading": "Subheading in under 10 words",
            "contact_email": "Contact email",
            "contact_phone": "Contact phone",
            "caption": "Create a caption: Promote a bestselling product for $99.99, under 300 characters, with hashtags",
        },
        "required": [],
    },
}


def get_template_variables(template_name: str) -> Dict[str, Any]:
    """
    Get the variable structure for a specific template.

    Args:
        template_name: Name of the template to get variables for

    Returns:
        Dictionary containing variable structure and example values

    Raises:
        ValueError: If template_name is not found in the registry
    """
    if template_name not in TEMPLATE_VARIABLES_REGISTRY:
        return TEMPLATE_VARIABLES_REGISTRY["default"]["variables"]
    return TEMPLATE_VARIABLES_REGISTRY[template_name]["variables"]


def get_required_variables(template_name: str) -> list[str]:
    """
    Get the list of required variables for a template.

    Args:
        template_name: Name of the template

    Returns:
        List of required variable names
    """
    template = get_template_variables(template_name)
    return template.get("required", [])


def get_available_templates() -> list[str]:
    """
    Get a list of all available template names.

    Returns:
        List of template names
    """
    return list(TEMPLATE_VARIABLES_REGISTRY.keys())
