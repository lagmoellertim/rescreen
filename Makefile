prepare:
	python -m build --wheel --no-isolation

install:
	python -m installer --destdir="${DESTDIR}" dist/*.whl
	mkdir -p ${DESTDIR}/usr/share/icons/
	install -m644 assets/icon_rounded.png ${DESTDIR}/usr/share/icons/rescreen.png
	desktop-file-install --dir ${DESTDIR}/usr/share/applications system/rescreen.desktop