import datetime, time, re
from pprint import pprint

from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.http import JsonResponse, Http404
from django.views.generic import UpdateView, CreateView, View, TemplateView

from django.db.models import Q, Sum, F
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic.dates import MonthArchiveView
from django.core.exceptions import PermissionDenied
from django.db.models import Sum, Count

from django.contrib.auth.models import User

from .forms import OperationForm, CategoryForm, FamilyForm
from .models import Category, Operation, Family

colors = [
    ['#A35EEB', '#EBB76A', '#525AEB', '#EAEB3B', '#46A5EB'],
    ['#0E966D', '#1CC40A', '#CCC900', '#E3A40B', '#D9550B'],
]


# Create your views here.
def get_category_by_ajax(request):
    """Получение категорий по ajax"""
    if request.user.is_anonymous:
        raise PermissionDenied
    if request.is_ajax():
        type_pay = request.GET.get('type_pay', 0)
        categories = list(
            Category.objects.filter((Q(user_id=None) | Q(user_id=request.user.id)) &
                                    Q(type_pay=type_pay)).values('id', 'name').order_by('name'))
        return JsonResponse({'categories': categories}, status=200)


def get_operation_by_ajax(request):
    if request.user.is_anonymous:
        raise PermissionDenied

    date_str_format = request.GET.get('month', datetime.datetime.now().strftime('%Y-%m'))
    year, month = map(int, date_str_format.split('-'))

    operations = Operation.objects.filter(user_id=request.user.id,
                                          date__month=month,
                                          date__year=year)

    total = operations.filter(category__type_pay=1).aggregate(total=Sum('value'))['total']
    total_cost = operations.filter(category__type_pay=0).aggregate(total=Sum('value'))['total']
    if total is None:
        total = 0
    if total_cost is None:
        total_cost = 0
    total -= total_cost

    operations = operations.values('id', 'value', 'description',
                                   'category__type_pay',
                                   'category__name', 'date').order_by('-date', '-id')
    return JsonResponse({'operations': list(operations), 'total': total})


def get_data_for_chart_family_by_ajax(request):
    """Получение данных для построения диаграммы. ajax"""
    if request.user.is_anonymous:
        raise PermissionDenied

    type_pay = int(request.GET.get('type_pay', 0))
    year = int(request.GET.get('year', datetime.datetime.now().year))
    month = int(request.GET.get('month', -1))

    family = Family.objects.get(users=request.user.id)
    data = Operation.objects.filter(category__type_pay=type_pay,
                                    user__in=family.users.all())
    if month == -1:
        data = data.filter(date__year=year)
    else:
        data = data.filter(date__year=year, date__month=month)

    categories = data.values(_category=F('category__name')).annotate(total=Sum('value'))
    categories = list(categories)

    users = data.values(_user=F('user__username')).annotate(total=Sum('value'))
    users = list(users)

    for i in range(len(categories)):
        item = categories[i]
        item.update({'color': colors[type_pay][i % len(colors[type_pay])]})

    for i in range(len(users)):
        item = users[i]
        item.update({'color': colors[type_pay][i % len(colors[type_pay])]})

    return JsonResponse({'categories': categories, 'users': users}, status=200)


class OperationView(LoginRequiredMixin, TemplateView):
    login_url = reverse_lazy('a-login')
    template_name = 'budget/list_operation_js.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        categories = Category.objects.filter(Q(user_id=None) | Q(user_id=self.request.user.id)).values('id', 'name')
        context.update({'categories': categories})
        return context


# def family_view(request):
#     if request.user.is_anonymous:
#         return redirect('/')
#
#     if request.method == 'POST':
#         uuid = request.POST.get('uuid', None)
#         if uuid and re.match(r'[a-z0-9]{8}-[a-z0-9]{4}-[a-z0-9]{4}-[a-z0-9]{4}-[a-z0-9]{12}', uuid) is not None:
#             family = Family.objects.get(uuid=uuid)
#             family.users.add(request.user)
#             return redirect('b-family')
#         form = FamilyForm(request.POST)
#         if form.is_valid():
#             form.instance.author = request.user
#             form.save()
#             form.instance.users.add(request.user)
#             return redirect('b-family')
#
#     families = Family.objects.filter(users=request.user)
#     context = {
#         'family': families[0] if families else None,
#     }
#
#     return render(request, 'budget/family.html', context=context)


class FamilyView(LoginRequiredMixin, View):
    login_url = reverse_lazy('a-login')

    def post(self, request):
        uuid = request.POST.get('uuid', None)
        if uuid and re.match(r'[a-z0-9]{8}-[a-z0-9]{4}-[a-z0-9]{4}-[a-z0-9]{4}-[a-z0-9]{12}', uuid) is not None:
            family = Family.objects.get(uuid=uuid)
            family.users.add(request.user)
            return redirect('b-family')
        form = FamilyForm(request.POST)
        if form.is_valid():
            form.instance.author = request.user
            form.save()
            form.instance.users.add(request.user)
            return redirect('b-family')
        return redirect('b-family')

    def get(self, request):
        families = Family.objects.filter(users=request.user)
        context = {
            'family': families[0] if families else None,
        }
        return render(request, 'budget/family.html', context=context)


def family_operation_view(request):
    if request.user.is_anonymous:
        return redirect('a-login')

    family = Family.objects.filter(users=request.user)
    if family.exists():
        family = family[0]
    else:
        return redirect('b-family')

    year = int(request.GET.get('year', datetime.datetime.now().year))
    month = int(request.GET.get('month', datetime.datetime.now().month))

    operations = Operation.objects.filter(user__in=family.users.all(),
                                          date__month=month,
                                          date__year=year).order_by('-date', '-id')
    total = operations.filter(category__type_pay=1).aggregate(total=Sum('value'))['total']
    total_cost = operations.filter(category__type_pay=0).aggregate(total=Sum('value'))['total']
    if total is None:
        total = 0
    if total_cost is None:
        total_cost = 0
    total -= total_cost

    context = {
        'family': family,
        'operations': operations,
        'total': total,
        'year': year,
        'month': str(month).zfill(2),
    }
    return render(request, 'budget/family_operation.html', context=context)


def delete_user_from_family(request, pk):
    user = User.objects.get(id=pk)
    family = Family.objects.get(users=user)
    if family.author == request.user or user == request.user:
        family.users.remove(user)
    return redirect('b-family')


# def delete_family(request):
#     family = Family.objects.get(author=request.user)
#     family.delete()
#     return redirect('b-family')


class DeleteFamilyView(LoginRequiredMixin, View):
    login_url = reverse_lazy('a-login')

    def get(self, request):
        family = Family.objects.get(author=request.user)
        family.delete()
        return redirect('b-family')


def get_data_for_chart(request):
    """Получение данных для построения диаграммы. ajax"""
    if request.user.is_anonymous:
        raise PermissionDenied

    type_pay = int(request.GET.get('type_pay', 0))
    year = int(request.GET.get('year', datetime.datetime.now().year))
    month = int(request.GET.get('month', -1))

    data = Operation.objects.values('category__name').filter(category__type_pay=type_pay,
                                                             user__id=request.user.id)
    # .annotate(total=(Sum('value')))
    if month == -1:
        data = data.filter(date__year=year)
    else:
        data = data.filter(date__year=year, date__month=month)
    data = data.annotate(total=(Sum('value')))
    data = list(data)

    for i in range(len(data)):
        item = data[i]
        item.update({'color': colors[type_pay][i % len(colors[type_pay])]})

    return JsonResponse({'data': data}, status=200)


# def view_chart(request):
#     """Отображание страницы с пустой диаграммой"""
#     return render(request, 'budget/chart.html')


class ChartView(LoginRequiredMixin, TemplateView):
    login_url = reverse_lazy('a-login')
    template_name = 'budget/chart.html'


class FamilyChartView(LoginRequiredMixin, TemplateView):
    login_url = reverse_lazy('a-login')
    template_name = 'budget/chart_family.html'

    def get(self, request):
        if not Family.objects.filter(users=request.user).exists():
            return redirect('b-family')
        return super().get(request)


def delete_category(request, pk):
    """Удаление категории. Вызов происходит при помощи ajax"""
    if request.user.is_anonymous:
        raise PermissionDenied
    category = Category.objects.get(id=pk)
    if category is not None:
        if category.user == request.user:
            category.delete()
            return JsonResponse({'result': 'ok'}, status=200)
        return JsonResponse({'result': 'bad'}, status=200)


def delete_operation(request, pk):
    """Удаление операции. Вызов происходит при помощи ajax"""
    if request.user.is_anonymous:
        raise PermissionDenied
    operation = Operation.objects.get(id=pk)
    if operation is not None:
        if operation.user == request.user:
            operation.delete()
            return JsonResponse({'result': 'ok'}, status=200)
        return JsonResponse({'result': 'bad'}, status=200)


# def category_view(request):
#     if request.user.is_anonymous:
#         return redirect('/')
#
#     form = CategoryForm(initial={'user_id': request.user.id})
#     if request.method == "POST":
#         bound_form = CategoryForm(request.POST)
#         if bound_form.is_valid():
#             bound_form.instance.user = request.user
#             bound_form.save()
#             return redirect('/category/')
#         else:
#             form = bound_form
#     category_list = Category.objects.filter(user_id=request.user.id).order_by('type_pay', 'name')
#     return render(request, 'budget/category.html', {'form': form, 'category_list': category_list})


def index(request):
    return render(request, 'budget/index.html')


# def operation_create(request):
#     if request.method == "POST":
#         bound_form = OperationForm(request.POST)
#         if bound_form.is_valid():
#             bound_form.instance.user_id = request.user.id
#             bound_form.save()
#             return redirect('/')
#         else:
#             return render(request, 'budget/index.html', {'form': bound_form})
#
#     if request.method == "GET":
#         form = OperationForm()
#         return render(request, 'budget/index.html', {'form': form})


# def update_operation(request, pk):
#     operation = Operation.objects.get(pk=pk)
#     form_data = {'type_pay': operation.category.type_pay, 'instance': operation.category_id}
#     form = OperationForm(instance=operation)
#
#     if request.method == "POST":
#         bound_form = OperationForm(request.POST, instance=operation)
#         if bound_form.is_valid():
#             bound_form.save()
#             return redirect('/operation/' + str(pk) + '/')
#
#     return render(request, 'budget/operation_update.html', {'form': form, 'form_data': form_data})


class OperationUpdate(LoginRequiredMixin, UpdateView):
    login_url = reverse_lazy('a-login')
    form_class = OperationForm
    model = Operation
    template_name = 'budget/operation_update.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        form_data = {'type_pay': self.object.category.type_pay, 'instance': self.object.category_id}
        context.update({'form_data': form_data})
        return context

    def get_form_kwargs(self):
        if self.object.user != self.request.user:
            raise PermissionDenied
        return super().get_form_kwargs()

    def get_success_url(self):
        return reverse_lazy('b-list-operation')


class OperationCreate(LoginRequiredMixin, CreateView):
    login_url = reverse_lazy('a-login')
    form_class = OperationForm
    model = Operation
    template_name = 'budget/operation_create.html'
    success_url = reverse_lazy('b-list-operation')

    def form_valid(self, form):
        form.instance.user_id = self.request.user.id
        return super().form_valid(form)

    def get_success_url(self):
        return self.request.POST.get('next', self.success_url)


class OperationListView(LoginRequiredMixin, MonthArchiveView):
    login_url = reverse_lazy('a-login')
    model = Operation
    template_name = 'budget/list_operation.html'
    context_object_name = 'list_operation'

    date_field = 'date'
    month_format = '%m'
    allow_empty = True

    def get_month(self):
        try:
            month = super().get_month()
        except Http404:
            month = datetime.datetime.now().strftime(self.get_month_format())
        return month

    def get_year(self):
        try:
            year = super().get_year()
        except Http404:
            year = datetime.datetime.now().strftime(self.get_year_format())
        return year

    def get_queryset(self):
        queryset = super().get_queryset()
        return queryset.filter(user_id=self.request.user.id).order_by('-date', '-id')

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        total = self.object_list.filter(category__type_pay=1).aggregate(total=Sum('value'))['total']
        if total is None:
            total = 0
        total_cost = self.object_list.filter(category__type_pay=0).aggregate(total=Sum('value'))['total']
        if total_cost is None:
            total_cost = 0
        total -= total_cost
        context.update({'total': total})
        return context


class CategoryCreateView(LoginRequiredMixin, CreateView):
    login_url = reverse_lazy('a-login')
    template_name = 'budget/category.html'
    form_class = CategoryForm
    model = Category
    success_url = reverse_lazy('b-category')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        category_list = Category.objects.filter(user_id=self.request.user.id).order_by('type_pay', 'name')
        context.update({'category_list': category_list})
        return context

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['initial'].update({'user_id': self.request.user.id})
        return kwargs

    def form_valid(self, form):
        form.instance.user_id = form.cleaned_data['user_id']
        return super().form_valid(form)
