# list all not used compoents, elemtns , pages
from api_lessons.models import LessonPage, LessonPageElement
from api_lessons.models.lesson_components.matching_component import MatchingComponentElementCouple, MatchingComponentElement
from lms.apps.resources.editor_v2.api.components_utils import COMPONENT_NAME_TO_ELEMENT_FIELD_NAME_DICT, \
    COMPONENT_NAME_TO_COMPONENT_MODEL_CLASS_DICT


def get_element_component(element: LessonPageElement):
    for key in COMPONENT_NAME_TO_ELEMENT_FIELD_NAME_DICT.keys():
        value = getattr(element, COMPONENT_NAME_TO_ELEMENT_FIELD_NAME_DICT[key], None)
        if value:
            return value, key
    return None, None


def collect():
    not_used_lesson_pages = LessonPage.objects.filter(lesson__isnull=True)
    not_used_elements = LessonPageElement.objects.filter(
        page__isnull=True,
    )
    used_components = []
    component_name_components_ids_list_map = dict()
    for i in COMPONENT_NAME_TO_COMPONENT_MODEL_CLASS_DICT.keys():
        component_name_components_ids_list_map[i] = []
    for lesson_page in LessonPage.objects.all():
        for el in lesson_page.elements.all():
            used_element_component_obj, component_type = get_element_component(el)
            if not used_element_component_obj:
                used_components.append({
                    "element": el,
                    "component": None,
                    "error": {
                        "message": "No component found",
                    }
                })
            else:
                used_components.append({
                    "element": el,
                    "component": used_element_component_obj,
                    "component_type": component_type,
                })
                component_name_components_ids_list_map[component_type].append(used_element_component_obj.id)

    component_name_components_qs_map = dict()
    for key in component_name_components_ids_list_map.keys():
        component_name_components_qs_map[key] = COMPONENT_NAME_TO_COMPONENT_MODEL_CLASS_DICT[key].objects.filter(
            id__in=component_name_components_ids_list_map[key]
        )

    not_used_component_name_components_qs_map = dict()
    for key in component_name_components_ids_list_map.keys():
        not_used_component_name_components_qs_map[key] = COMPONENT_NAME_TO_COMPONENT_MODEL_CLASS_DICT[key].objects.exclude(
            id__in=component_name_components_ids_list_map[key]
        )

    not_used_component_name_components_ids_map = dict()
    for i in not_used_component_name_components_qs_map.keys():
        not_used_component_name_components_ids_map[i] = list(
            not_used_component_name_components_qs_map[i].values_list(
                "id", flat=True
            )
        )

    all_couples = MatchingComponentElementCouple.objects.all()
    used_elements_ids = set()
    for couple in all_couples:
        used_elements_ids.add(couple.first_element_id)
        used_elements_ids.add(couple.second_element_id)
    not_used_matching_component_elements_ids = MatchingComponentElement.objects.exclude(
        id__in=used_elements_ids
    ).values_list("id", flat=True)

    context = {
        "not_used_lesson_pages": {
            "ids": list(not_used_lesson_pages.values_list("id", flat=True)),
        },
        "not_used_elements": {
            "ids": list(not_used_elements.values_list("id", flat=True)),
        },
        "not_used_components": not_used_component_name_components_ids_map,
        "not_used_matching_component_elements": {
            "ids": list(not_used_matching_component_elements_ids),
        },
    }
    return context
