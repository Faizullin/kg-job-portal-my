from django.utils.translation import gettext_lazy as _
from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from django.db import transaction
from api_lessons.models.lesson_components.matching_component import (
    MatchingComponent,
    MatchingComponentElement,
    MatchingComponentElementCouple,
)
from .utils import components_elements_qs, getUid
from collections import Counter

# ─────────────────────────────  HELPERS  ──────────────────────────────


def get_image(obj):
    return None if not obj.image else {"url": obj.image.url}


def _build_representation(component: MatchingComponent) -> dict:
    """
    Shared read-side formatter for list / detail responses.
    """
    couples_qs = component.element_couples.all().select_related(
        "first_element", "second_element"
    )

    elem_map = {}
    for c in couples_qs:
        elem_map[getUid(c.first_element_id)] = c.first_element
        elem_map[getUid(c.second_element_id)] = c.second_element

    return {
        "id": component.id,
        "title": component.title,
        "elements": [
            {
                "id": e.id,
                "uid": getUid(e.id),
                "text": e.text,
                "image": get_image(e),
            }
            for e in elem_map.values()
        ],
        "couples": [
            {
                "first_element": getUid(c.first_element_id),
                "second_element": getUid(c.second_element_id),
            }
            for c in couples_qs
        ],
    }


# ─────────────────────────────  READ-ONLY  ─────────────────────────────
class MatchingComponentElementRO(serializers.ModelSerializer):
    uid = serializers.SerializerMethodField()

    class Meta:
        model = MatchingComponentElement
        fields = ("id", "uid", "text", "image")

    def getgetUid(self, obj):
        return getUid(obj.id)


class MatchingComponentListSerializer(serializers.ModelSerializer):
    class Meta:
        model = MatchingComponent
        fields = ("id", "title")


class MatchingComponentDetailSerializer(serializers.Serializer):
    def to_representation(self, instance):
        return _build_representation(instance)


# ─────────────────────────────  WRITE SCHEMAS  ─────────────────────────
class MatchingElementInput(serializers.Serializer):
    """
    • **uid** (required) – client-side key (string)
    • **id** (optional) – existing element PK when updating
    """

    uid = serializers.CharField()
    id = serializers.IntegerField(required=False)
    text = serializers.CharField(required=False, allow_blank=True)
    image_file = serializers.ImageField(required=False)

    def validate(self, attrs):
        if not attrs.get("uid"):
            raise ValidationError(_("Element uid is required."))
        return attrs


class MatchingCoupleInput(serializers.Serializer):
    first_element = serializers.CharField()
    second_element = serializers.CharField()


# ─────────────────────────  CREATE / UPDATE  ──────────────────────────
class MatchingComponentCreateUpdateSerializer(serializers.ModelSerializer):
    elements = MatchingElementInput(many=True, write_only=True)
    couples = MatchingCoupleInput(many=True, write_only=True)

    class Meta:
        model = MatchingComponent
        fields = ("id", "title", "elements", "couples")

    # ----------  internal helpers ----------
    def _get_or_create_elements(self, elements_data):
        """
        Returns a dict  { uid ➜ MatchingComponentElement instance }
        New objects are bulk-created; existing objects are updated and saved.
        """
        new_instances = []
        updated_instances = []
        uid_map = {}

        for elem in elements_data:
            uid = elem["uid"]  # always present
            instance = None

            # existing element?
            if elem.get("id"):
                try:
                    instance = MatchingComponentElement.objects.get(pk=elem["id"])
                except MatchingComponentElement.DoesNotExist:
                    raise ValidationError(_(f"Element id {elem['id']} not found"))

                # Track if any changes were made
                changed = False
                if "text" in elem and instance.text != elem["text"]:
                    instance.text = elem["text"]
                    changed = True

                if "image_file" in elem and instance.image != elem["image_file"]:
                    # Delete old image if replacing with new one
                    if instance.image:
                        instance.image.delete(save=False)
                    instance.image = elem["image_file"]
                    changed = True

                # Add to update list if changed
                if changed:
                    updated_instances.append(instance)
            else:
                # new element (save later)
                instance = MatchingComponentElement(
                    text=elem.get("text", ""),
                    image=elem.get("image_file"),
                )
                new_instances.append(instance)

            uid_map[uid] = instance

        # create new elements in bulk
        if new_instances:
            MatchingComponentElement.objects.bulk_create(new_instances)

        # save updated elements
        for instance in updated_instances:
            instance.save()

        return uid_map

    def _validate_elements_used_in_couples(self, elements_data, couples_data):
        """
        Validate that all provided elements are used in at least one couple.
        Raises ValidationError if any element is not referenced in couples.
        """
        element_uids = {elem["uid"] for elem in elements_data}
        used_uids = set()

        for couple in couples_data:
            used_uids.add(couple["first_element"])
            used_uids.add(couple["second_element"])

        unused_uids = element_uids - used_uids
        if unused_uids:
            unused_list = ", ".join(sorted(unused_uids))
            raise ValidationError(
                _(f"The following elements are not used in any couples: {unused_list}")
            )

    def _validate_one_to_one_couples(self, couples_data):
        """
        Validates that each element appears at most once in each role (first or second).
        An element can appear multiple times only if it's always in the same position.
        """
        first_element_uids = []
        second_element_uids = []

        for couple in couples_data:
            first_element_uids.append(couple["first_element"])
            second_element_uids.append(couple["second_element"])

        # Count frequency of each uid in each position

        first_counts = Counter(first_element_uids)
        second_counts = Counter(second_element_uids)

        # An element should not appear in both roles
        duplicates = []
        all_uids = set(first_counts.keys()) | set(second_counts.keys())

        for uid in all_uids:
            if first_counts[uid] > 1 or second_counts[uid] > 1:
                duplicates.append(uid)

        if duplicates:
            duplicate_list = ", ".join(sorted(duplicates))
            raise ValidationError(
                _(
                    f"The following elements appear in both first and second positions across couples, which is not allowed: {duplicate_list}"
                )
            )

    def _cleanup_unused_elements_and_couples(self, component, uid_map, couples_data):
        """
        Delete elements and couples that are no longer used after update.
        Compares current data with what should remain based on uid_map.
        """
        # Get IDs of elements that should remain
        remaining_element_ids = {
            instance.id for instance in uid_map.values() if instance.id
        }

        # Delete unused elements (and their associated image files)
        used_elements = components_elements_qs(component)
        unused_elements = used_elements.exclude(id__in=remaining_element_ids)
        print(
            "cleanup_unused_elements_and_couples: remaining_element_ids",
            used_elements,
            "-",
            remaining_element_ids,
            "=",
            unused_elements,
        )

        for element in unused_elements:
            if element.image:
                element.image.delete(save=False)  # Delete image file from storage
        unused_elements.delete()

        # Delete all existing couples - they will be recreated in _sync_couples
        component.element_couples.all().delete()

        # Synchronize couples to match `couples_data`
        desired_pairs = set()
        for c in couples_data:
            try:
                first = uid_map[c["first_element"]].id
                second = uid_map[c["second_element"]].id
            except KeyError as k:
                raise ValidationError(_(f"Couple references unknown uid: {k.args[0]}"))
            desired_pairs.add((first, second))

        current_pairs = {
            (c.first_element_id, c.second_element_id): c.id
            for c in component.element_couples.all().only(
                "id", "first_element_id", "second_element_id"
            )
        }

        # delete couples no longer wanted
        stale_ids = [
            cid for pair, cid in current_pairs.items() if pair not in desired_pairs
        ]
        if stale_ids:
            MatchingComponentElementCouple.objects.filter(id__in=stale_ids).delete()

        # add new couples
        new_objs = [
            MatchingComponentElementCouple(
                component=component,
                first_element_id=p[0],
                second_element_id=p[1],
            )
            for p in desired_pairs
            if p not in current_pairs
        ]
        if new_objs:
            MatchingComponentElementCouple.objects.bulk_create(new_objs)

    def _sync_couples(self, component, couples_data, uid_map):
        """
        Synchronize couples based on provided data and uid_map.
        Creates new couples or updates existing ones.
        """
        desired_pairs = set()
        for c in couples_data:
            try:
                first = uid_map[c["first_element"]].id
                second = uid_map[c["second_element"]].id
            except KeyError as k:
                raise ValidationError(_(f"Couple references unknown uid: {k.args[0]}"))
            desired_pairs.add((first, second))

        current_pairs = {
            (c.first_element_id, c.second_element_id): c.id
            for c in component.element_couples.all().only(
                "id", "first_element_id", "second_element_id"
            )
        }

        stale_ids = [
            cid for pair, cid in current_pairs.items() if pair not in desired_pairs
        ]
        if stale_ids:
            MatchingComponentElementCouple.objects.filter(id__in=stale_ids).delete()

        new_objs = [
            MatchingComponentElementCouple(
                component=component,
                first_element_id=p[0],
                second_element_id=p[1],
            )
            for p in desired_pairs
            if p not in current_pairs
        ]
        print(
            "sync_couples: desired_pairs",
            desired_pairs,
            "-",
            current_pairs,
            "=",
            new_objs,
        )
        if new_objs:
            MatchingComponentElementCouple.objects.bulk_create(new_objs)

    # ----------  create ----------
    @transaction.atomic
    def create(self, validated_data):
        elems_in = validated_data.pop("elements")
        couples_in = validated_data.pop("couples")

        # Validate one-to-one mapping in couples
        self._validate_one_to_one_couples(couples_in)

        # Validate that all elements are used in couples
        self._validate_elements_used_in_couples(elems_in, couples_in)

        component = MatchingComponent.objects.create(title=validated_data["title"])
        uid_map = self._get_or_create_elements(elems_in)
        self._sync_couples(component, couples_in, uid_map)
        return component

    # ----------  update ----------
    @transaction.atomic
    def update(self, instance, validated_data):
        instance.title = validated_data.get("title", instance.title)

        elems_in = validated_data.pop("elements", [])
        couples_in = validated_data.pop("couples", [])

        # Validate one-to-one mapping in couples
        if couples_in:  # Only validate if couples are provided
            self._validate_one_to_one_couples(couples_in)

        # Validate that all elements are used in couples
        if elems_in:  # Only validate if elements are provided
            self._validate_elements_used_in_couples(elems_in, couples_in)

        uid_map = self._get_or_create_elements(elems_in)

        # Clean up unused elements and couples before syncing new ones
        if elems_in:  # Only cleanup if elements data is provided
            self._cleanup_unused_elements_and_couples(instance, uid_map, couples_in)

        self._sync_couples(instance, couples_in, uid_map)

        instance.save()
        return instance

    # ----------  out ----------
    def to_representation(self, instance):
        return _build_representation(instance)


class MatchingComponentFileControlSerializer(serializers.Serializer):
    ACTION_CHOICES = (
        ("upload", "Upload"),
        ("remove", "Remove"),
    )
    file_action = serializers.ChoiceField(choices=ACTION_CHOICES)
    file = serializers.FileField(required=False, allow_null=True)
    object_id = serializers.IntegerField()
    element_id = serializers.IntegerField()

    def validate(self, data):
        file_action = data.get("file_action")
        file = data.get("file", None)

        if file_action == "upload":
            if file is None:
                raise serializers.ValidationError(
                    {"file": "File is required for upload."}
                )

            # Optional: Include format and size validation here
            self.validate_file_format(file)
            self.validate_file_size(file)

        elif file_action == "remove":
            if file:
                raise serializers.ValidationError(
                    {"file": "File should not be provided for remove."}
                )

        return data

    def validate_file_format(self, file):
        allowed_mime_types = [
            "image/jpeg",
            "image/png",
        ]
        if file.content_type not in allowed_mime_types:
            raise serializers.ValidationError({"file": "Unsupported file format."})

    def validate_file_size(self, file, file_size_limit_b=None):
        if file_size_limit_b is None:
            file_size_limit_b = 10 * 1024 * 1024  # Default to 10MB
        max_size_mb = int(file_size_limit_b / (1024 * 1024))  # Convert bytes to MB
        if file.size > file_size_limit_b:
            raise serializers.ValidationError(
                {"file": f"File size exceeds {max_size_mb}MB."}
            )
