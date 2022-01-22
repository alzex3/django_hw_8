import pytest
import random
from rest_framework.test import APIClient
from model_bakery import baker
from django.urls import reverse, resolve

from students.models import Student, Course


@pytest.fixture
def client():
    return APIClient()


@pytest.fixture
def students_factory():

    def factory(*args, **kwargs):
        return baker.make(Student, *args, **kwargs)

    return factory


@pytest.fixture
def courses_factory():

    def factory(*args, **kwargs):
        return baker.make(Course, *args, **kwargs)

    return factory


@pytest.mark.django_db
def test_course(client, students_factory, courses_factory):
    # Arrange
    students_set = students_factory(_quantity=3)
    course = courses_factory(students=students_set)

    # Act
    url = reverse('courses-detail', kwargs={'pk': course.id})
    resp = client.get(url)

    # Assert
    assert resp.status_code == 200

    resp_course = resp.json()
    assert resp_course['name'] == course.name

    for student in course.students.all():
        assert student.id in resp_course['students']


@pytest.mark.django_db
def test_courses(client, students_factory, courses_factory):
    # Arrange
    students_set = students_factory(_quantity=15)
    courses = courses_factory(students=students_set, _quantity=10)

    # Act
    url = reverse('courses-list')
    resp = client.get(url)

    # Assert
    assert resp.status_code == 200

    resp_courses = resp.json()
    for i, resp_course in enumerate(resp_courses):
        assert resp_course['name'] == courses[i].name

        for student in courses[i].students.all():
            assert student.id in resp_course['students']


@pytest.mark.django_db
def test_courses_filter_id(client, students_factory, courses_factory):
    # Arrange
    students_set = students_factory(_quantity=5)
    courses = courses_factory(students=students_set, _quantity=10)
    course = random.choice(courses)

    # Act
    url = reverse('courses-list') + '?id=' + str(course.id)
    resp = client.get(url)

    # Assert
    assert resp.status_code == 200

    resp_course = resp.json()[0]
    assert resp_course['name'] == course.name

    for student in course.students.all():
        assert student.id in resp_course['students']


@pytest.mark.django_db
def test_courses_filter_name(client, students_factory, courses_factory):
    # Arrange
    students_set = students_factory(_quantity=15)
    courses = courses_factory(students=students_set, _quantity=10)
    course = random.choice(courses)

    # Act
    url = reverse('courses-list') + '?name=' + course.name
    resp = client.get(url)

    # Assert
    assert resp.status_code == 200

    resp_course = resp.json()[0]
    assert resp_course['name'] == course.name

    for student in course.students.all():
        assert student.id in resp_course['students']


@pytest.mark.django_db
def test_course_post(client):
    # Arrange
    course = {
        'name': 'Python',
    }

    # Act
    url = reverse('courses-list')
    resp = client.post(url, course)

    # Assert
    assert resp.status_code == 201

    resp_course = resp.json()
    assert resp_course['name'] == course['name']


@pytest.mark.django_db
def test_course_patch(client, students_factory, courses_factory):
    # Arrange
    students_set = students_factory(_quantity=3)
    course = courses_factory(students=students_set)

    patch_course = {
        'name': 'Python',
    }

    # Act
    url = reverse('courses-detail', kwargs={'pk': course.id})
    resp = client.patch(url, patch_course)

    # Assert
    assert resp.status_code == 200

    resp_course = resp.json()
    assert resp_course['name'] == patch_course['name']

    for student in course.students.all():
        assert student.id in resp_course['students']


@pytest.mark.django_db
def test_course_delete(client, students_factory, courses_factory):
    # Arrange
    students_set = students_factory(_quantity=15)
    courses = courses_factory(students=students_set, _quantity=10)
    course = random.choice(courses)

    # Act
    url = reverse('courses-detail', kwargs={'pk': course.id})
    resp = client.delete(url)

    # Assert
    assert resp.status_code == 204
    assert course not in Course.objects.all()
