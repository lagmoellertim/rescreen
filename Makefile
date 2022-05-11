prepare:
	#/usr/bin/python3 -m build --wheel --no-isolation
	/usr/bin/python3 setup.py build

install:
	#/usr/bin/python3 -m installer --destdir="${DESTDIR}" packaging/*.whl
	/usr/bin/python3 setup.py install --root="${DESTDIR}" --optimize=1

	install -m644 -D assets/icon_rounded.png ${DESTDIR}/usr/share/icons/rescreen.png
	desktop-file-install --dir ${DESTDIR}/usr/share/applications system/rescreen.desktop
	install -m755 -D system/rescreen.service ${DESTDIR}/usr/lib/systemd/system/rescreen.service

