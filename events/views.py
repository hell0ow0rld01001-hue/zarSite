import base64
import io
import qrcode
import qrcode.image.svg
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from .models import Event, EventParticipant


def generate_qr_svg_base64(url: str) -> str:
    factory = qrcode.image.svg.SvgPathImage
    img = qrcode.make(url, image_factory=factory, box_size=10, border=2)
    buffer = io.BytesIO()
    img.save(buffer)
    svg_base64 = base64.b64encode(buffer.getvalue()).decode("utf-8")
    return f"data:image/svg+xml;base64,{svg_base64}"


def event_detail_view(request, pk):
    event = get_object_or_404(Event, pk=pk)

    if request.method == "POST":
        full_name = request.POST.get("full_name", "").strip()
        phone_number = request.POST.get("phone_number", "").strip()

        if full_name and phone_number:
            EventParticipant.objects.create(
                event=event,
                full_name=full_name,
                phone_number=phone_number,
            )
            messages.success(request, "اطلاعات شما با موفقیت در رویداد ثبت شد")
            return redirect("event_detail", pk=event.pk)

        messages.error(request, "لطفاً نام و شماره تماس را کامل وارد کنید")

    current_url = request.build_absolute_uri()
    qr_data_uri = generate_qr_svg_base64(current_url)

    return render(
        request,
        "event_detail.html",
        {
            "event": event,
            "qr_data_uri": qr_data_uri,
            "current_url": current_url,
        },
    )
