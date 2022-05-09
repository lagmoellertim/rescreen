prepare:
	python -m build --wheel --no-isolation

install:
	python -m installer --destdir="${DESTDIR}" dist/*.whl
	install -m644 -D assets/icon_rounded.png ${DESTDIR}/usr/share/icons/rescreen.png
	desktop-file-install --dir ${DESTDIR}/usr/share/applications system/rescreen.desktop
	install -m755 -D system/rescreen.service ${DESTDIR}/usr/lib/systemd/system/rescreen.service