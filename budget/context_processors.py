from django.urls import reverse_lazy


def link_of_my_finance(request):
    return {'link_myfinance':
                [reverse_lazy('b-list-operation'),
                 reverse_lazy('b-chart'),
                 reverse_lazy('b-category')]
            }


def link_of_my_family(request):
    return {'link_myfamily':
                [reverse_lazy('b-family'),
                 reverse_lazy('b-family-operation'),
                 reverse_lazy('b-family-chart'),
                 ]
            }
