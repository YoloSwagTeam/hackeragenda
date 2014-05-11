def filter_events(request, queryset):
    if request.GET.getlist("source"):
        queryset = queryset.filter(source__in=request.GET.getlist("source"))

    if request.GET.getlist("exclude_source"):
        queryset = queryset.exclude(source__in=request.GET.getlist("exclude_source"))

    if request.GET.getlist("tag"):
        queryset = queryset.filter(tags__name__in=request.GET.getlist("tag"))

    if request.GET.getlist("exclude_tag"):
        queryset = queryset.exclude(tags__name__in=request.GET.getlist("exclude_tag"))

    return queryset
