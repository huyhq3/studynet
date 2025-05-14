from random import randint

from django.contrib.auth.models import User
from django.utils.text import slugify
from rest_framework.response import Response
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from .serializers import CourseListSerializer, LessonListSerializer, CategorySerializer, QuizSerializer, \
    CommentsSerializer, UserSerializer, CourseDetailSerializer
from .models import Course, Category, Lesson, Comment


@api_view(['POST'])
def create_course(request):
    status = request.data.get('status')
    print(request.data)
    if status == 'published':
        status = 'draft'

    course = Course.objects.create(
        title=request.data.get('title'),
        slug='%s-%s' % (slugify(request.data.get('title')), randint(1000, 10000)),
        short_description=request.data.get('short_description'),
        long_description=request.data.get('long_description'),
        status=status,
        created_by=request.user
    )

    for id in request.data.get('categories'):
        course.categories.add(id)

    course.save()

    # Lesson
    for lesson in request.data.get('lessons'):
        tmp_lesson = Lesson.objects.create(
            course=course,
            title=lesson.get('title'),
            slug=slugify(lesson.get('title')),
            short_description=lesson.get('short_description'),
            long_description=lesson.get('long_description'),
            status=Lesson.DRAFT
        )

    return Response({'course_id': course.id})


@api_view(['PUT'])
def update_course(request, slug):
    try:
        course = Course.objects.get(slug=slug, created_by=request.user)
    except Course.DoesNotExist:
        return Response({'error': 'Course not found or permission denied'}, status=404)

    data = request.data

    course.title = data.get('title', course.title)
    course.short_description = data.get('short_description', course.short_description)
    course.long_description = data.get('long_description', course.long_description)

    status = data.get('status', course.status)
    if status == 'published':
        course.status = 'draft'
    else:
        course.status = status

    if 'categories' in data:
        course.categories.set(data['categories'])

    course.save()

    return Response({'message': 'Course updated successfully', 'course_id': course.id})


@api_view(['POST'])
def create_lesson(request, course_slug):
    try:
        course = Course.objects.get(slug=course_slug, created_by=request.user)
    except Course.DoesNotExist:
        return Response({'error': 'Course not found or permission denied'}, status=404)

    data = request.data

    lesson = Lesson.objects.create(
        course=course,
        title=data.get('title'),
        slug=slugify(data.get('title')),
        short_description=data.get('short_description'),
        long_description=data.get('long_description'),
        status=Lesson.DRAFT
    )

    return Response({'message': 'Lesson created', 'lesson_id': lesson.id})


@api_view(['PUT'])
def update_lesson(request, course_slug, lesson_slug):
    try:
        course = Course.objects.get(slug=course_slug, created_by=request.user)
        lesson = Lesson.objects.get(slug=lesson_slug, course=course)
    except (Course.DoesNotExist, Lesson.DoesNotExist):
        return Response({'error': 'Lesson or Course not found or permission denied'}, status=404)

    data = request.data

    lesson.title = data.get('title', lesson.title)
    lesson.slug = slugify(lesson.title)
    lesson.short_description = data.get('short_description', lesson.short_description)
    lesson.long_description = data.get('long_description', lesson.long_description)
    lesson.status = data.get('status', lesson.status)

    lesson.save()

    return Response({'message': 'Lesson updated successfully', 'lesson_id': lesson.id})


# return the first quiz
# @api_view(['GET'])
# def get_quiz(request, course_slug, lesson_slug):
#     lesson = Lesson.objects.get(slug=lesson_slug)
#     quiz = lesson.quizzes.first()
#     serializer = QuizSerializer(quiz)
#     return Response(serializer.data)


@api_view(['GET'])
def get_quiz(request, course_slug, lesson_slug):
    lesson = Lesson.objects.get(slug=lesson_slug)
    quizzes = lesson.quizzes.all()
    serializer = QuizSerializer(quizzes, many=True)
    return Response(serializer.data)


@api_view(['GET'])
@authentication_classes([])
@permission_classes([])
def get_categories(request):
    categories = Category.objects.all()
    serializer = CategorySerializer(categories, many=True)
    return Response(serializer.data)


@api_view(['GET'])
@authentication_classes([])
@permission_classes([])
def get_front_courses(request):
    courses = Course.objects.filter(status=Course.PUBLISHED)
    serializer = CourseListSerializer(courses, many=True)
    return Response(serializer.data)


@api_view(['GET'])
@authentication_classes([])
@permission_classes([])
def get_courses(request):
    category_id = request.GET.get('category_id', '')
    courses = Course.objects.filter(status=Course.PUBLISHED)
    if category_id:
        courses = courses.filter(categories__in=[int(category_id)])

    serializer = CourseListSerializer(courses, many=True)
    return Response(serializer.data)


@api_view(['GET'])
def get_course(request, slug):
    course = Course.objects.filter(status=Course.PUBLISHED).get(slug=slug)
    course_serializer = CourseDetailSerializer(course)
    lesson_serializer = LessonListSerializer(course.lessons.all(), many=True)

    if request.user.is_authenticated:
        course_data = course_serializer.data
    else:
        course_data = {}

    return Response({
        'course': course_data,
        'lessons': lesson_serializer.data
    })


@api_view(['GET'])
def get_comments(request, course_slug, lesson_slug):
    lesson = Lesson.objects.get(slug=lesson_slug)
    serializer = CommentsSerializer(lesson.comments.all(), many=True)
    return Response(serializer.data)


@api_view(['POST'])
def add_comment(request, course_slug, lesson_slug):
    data = request.data
    course = Course.objects.get(slug=course_slug)
    lesson = Lesson.objects.get(slug=lesson_slug)
    comment = Comment.objects.create(course=course, lesson=lesson, name=data.get('name'), content=data.get('content'),
                                     created_by=request.user)
    serializer = CommentsSerializer(comment)
    return Response(serializer.data)


@api_view(['GET'])
def get_author_courses(request, user_id):
    user = User.objects.get(pk=user_id)
    courses = user.courses.filter(status=Course.PUBLISHED)

    user_serializer = UserSerializer(user, many=False)
    courses_serializer = CourseListSerializer(courses, many=True)

    return Response({
        'courses': courses_serializer.data,
        'created_by': user_serializer.data
    })
