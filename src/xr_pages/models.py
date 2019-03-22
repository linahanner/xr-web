from django.contrib.auth.models import Group
from django.db import models, transaction
from django.utils.translation import ugettext as _
from wagtail.admin.edit_handlers import StreamFieldPanel, FieldPanel, MultiFieldPanel
from wagtail.core.fields import StreamField
from wagtail.core.models import Page, Collection

from .blocks import ContentBlock
from .services import (
    get_or_create_or_update_page_auth_group_for_local_group_page,
    add_group_page_permission,
    get_document_permission,
    add_group_collection_permission,
    get_image_permission,
    get_or_create_or_update_page_auth_group_for_home_page,
    get_or_create_or_update_event_auth_group_for_home_page,
    get_or_create_or_update_event_auth_group_for_local_group_page,
)


class HomePage(Page):
    template = "xr_pages/pages/home.html"
    content = StreamField(ContentBlock, blank=True)
    group_name = models.CharField(max_length=50, default="Deutschland")
    group_email = models.EmailField(null=True, blank=True)

    content_panels = Page.content_panels + [StreamFieldPanel("content")]
    settings_panels = Page.settings_panels + [
        MultiFieldPanel(
            [FieldPanel("group_name"), FieldPanel("group_email")],
            heading=_("Regional Group settings"),
        )
    ]

    parent_page_types = []
    is_creatable = False

    @property
    def xr_group_name(self):
        return "XR %s" % self.group_name

    def clean(self):
        if not self.group_name:
            self.group_name = self.title

    @transaction.atomic
    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)

        # update regional page auth groups
        get_or_create_or_update_page_auth_group_for_home_page(
            self.specific, "Page Moderators"
        )
        get_or_create_or_update_page_auth_group_for_home_page(
            self.specific, "Page Editors"
        )

        # update regional event auth groups
        get_or_create_or_update_event_auth_group_for_home_page(
            self.specific, "Event Moderators"
        )
        get_or_create_or_update_event_auth_group_for_home_page(
            self.specific, "Event Editors"
        )


class HomeSubPage(Page):
    template = "xr_pages/pages/home_sub.html"
    content = StreamField(ContentBlock, blank=True)

    content_panels = Page.content_panels + [StreamFieldPanel("content")]

    parent_page_types = ["HomePage"]

    @transaction.atomic
    def save(self, *args, **kwargs):
        is_new = self.id is None

        super().save(*args, **kwargs)

        # we only need to add permissions on page creation
        if is_new:
            home_page = HomePage.objects.ancestor_of(self).live().get()

            regional_moderators_group = Group.objects.get(
                name="%s Page Moderators" % home_page.group_name
            )
            regional_editors_group = Group.objects.get(
                name="%s Page Editors" % home_page.group_name
            )

            # Moderators
            for permission_type in ["add", "edit", "publish"]:
                add_group_page_permission(
                    regional_moderators_group, self, permission_type
                )

            # Editors
            for permission_type in ["add", "edit"]:
                add_group_page_permission(regional_editors_group, self, permission_type)


class LocalGroupListPage(Page):
    template = "xr_pages/pages/local_group_list.html"
    content = StreamField(ContentBlock, blank=True)

    content_panels = Page.content_panels + [StreamFieldPanel("content")]

    parent_page_types = []
    is_creatable = False

    def get_context(self, request, *args, **kwargs):
        context = super().get_context(request, *args, **kwargs)
        context["local_groups"] = (
            LocalGroupPage.objects.child_of(self).live().order_by("-title")
        )
        return context


class LocalGroupPage(Page):
    template = "xr_pages/pages/local_group.html"
    content = StreamField(ContentBlock, blank=True)
    name = models.CharField(
        max_length=50,
        default="",
        unique=True,
        help_text=_(
            "The unique name for the local group. "
            "Used as label for links referring to this page. "
            'Enter a name without leading "XR ".'
        ),
    )
    email = models.EmailField(null=True, blank=True)
    # TODO: move state choices to settings
    STATE_CHOICES = (
        ("BW", "Baden-Württemberg"),
        ("BY", "Bayern"),
        ("BE", "Berlin"),
        ("BB", "Brandenburg"),
        ("HB", "Bremen"),
        ("HH", "Hamburg"),
        ("HE", "Hessen"),
        ("MV", "Mecklenburg-Vorpommern"),
        ("NI", "Niedersachsen"),
        ("NW", "Nordrhein-Westfalen"),
        ("RP", "Rheinland-Pfalz"),
        ("SL", "Saarland"),
        ("SN", "Sachsen"),
        ("ST", "Sachsen-Anhalt"),
        ("SH", "Schleswig-Holstein"),
        ("TH", "Thüringen"),
    )
    state = models.CharField(
        max_length=50, choices=STATE_CHOICES, null=True, blank=True
    )

    content_panels = Page.content_panels + [StreamFieldPanel("content")]
    settings_panels = Page.settings_panels + [
        MultiFieldPanel(
            [FieldPanel("name"), FieldPanel("email"), FieldPanel("state")],
            heading=_("Local Group settings"),
        )
    ]

    parent_page_types = ["LocalGroupListPage"]

    @property
    def xr_name(self):
        return "XR %s" % self.name

    @property
    def event_group(self):
        if self.event_group_set.all().exists:
            return self.event_group_set.first()
        return None

    @transaction.atomic
    def save(self, *args, **kwargs):
        is_new = self.id is None

        super().save(*args, **kwargs)

        # update local page group names
        moderators_group = get_or_create_or_update_page_auth_group_for_local_group_page(
            self, "Page Moderators"
        )
        editors_group = get_or_create_or_update_page_auth_group_for_local_group_page(
            self, "Page Editors"
        )

        if self.event_group:
            # update local event group names
            get_or_create_or_update_event_auth_group_for_local_group_page(
                self, "Event Moderators"
            )
            get_or_create_or_update_event_auth_group_for_local_group_page(
                self, "Event Editors"
            )

        # we only need to add page permissions on page creation
        if is_new:
            collection = Collection.objects.get(name="Common")

            # Moderators
            for permission_type in ["add", "edit", "publish"]:
                add_group_page_permission(moderators_group, self, permission_type)

            for codename in ["add_document", "change_document", "delete_document"]:
                add_group_collection_permission(
                    moderators_group, collection, get_document_permission(codename)
                )
            for codename in ["add_image", "change_image", "delete_image"]:
                add_group_collection_permission(
                    moderators_group, collection, get_image_permission(codename)
                )

            # Editors
            for permission_type in ["add", "edit"]:
                add_group_page_permission(editors_group, self, permission_type)

            add_group_collection_permission(
                editors_group, collection, get_document_permission("add_document")
            )
            add_group_collection_permission(
                editors_group, collection, get_image_permission("add_image")
            )


class LocalGroupSubPage(Page):
    template = "xr_pages/pages/local_group_sub.html"
    content = StreamField(ContentBlock, blank=True)

    content_panels = Page.content_panels + [StreamFieldPanel("content")]

    parent_page_types = ["LocalGroupPage"]

    def get_context(self, request, *args, **kwargs):
        context = super().get_context(request, *args, **kwargs)
        context["parent_page"] = self.get_parent()
        context["local_group_page"] = self.get_parent()
        return context
