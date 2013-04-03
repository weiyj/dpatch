%define debug_package %{nil}

Summary: Automated Linux Kernel Patch Generate Engine
Name: dpatch
Version: 0.8
Release: 0%{?dist}
License: GPLv2
Group: System Environment/Base
URL: https://github.com/weiyj/dpatch
Source0: https://github.com/weiyj/dpatch/archive/dpatch-%{version}.tar.gz
BuildRoot: %{_tmppath}/%{name}-%{version}-%{release}-root
Requires: git
Requires: Django
Requires: coccinelle
Requires: gcc make
BuildArch: noarch
ExcludeArch: ppc64 s390 s390x

%package core
Summary: Automated Linux Kernel Patch Generate Engine Core
Group: System Environment/Base

%package webui
Summary: Automated Linux Kernel Patch Generate Engine Web UI
Group: Applications/Internet

Requires: dpatch-core
Requires: httpd mod_wsgi
Requires: git-email

%description
Automated Linux Kernel Patch Generate Engine

%description core
Automated Linux Kernel Patch Generate Engine Core

%description webui
Automated Linux Kernel Patch Generate Engine Web UI

%prep
%setup -q

%build

%install
rm -rf $RPM_BUILD_ROOT

%{__install} -d $RPM_BUILD_ROOT/usr/share/dpatch
%{__install} -d $RPM_BUILD_ROOT/usr/share/dpatch/bin
%{__install} -d $RPM_BUILD_ROOT/usr/share/dpatch/dpatch
%{__install} -d $RPM_BUILD_ROOT/usr/share/dpatch/dpatch/views
%{__install} -D manage.py $RPM_BUILD_ROOT/usr/share/dpatch/
%{__install} -D bin/*.py $RPM_BUILD_ROOT/usr/share/dpatch/bin/
%{__install} -D bin/*.sh $RPM_BUILD_ROOT/usr/share/dpatch/bin/
%{__install} -D dpatch/*.py $RPM_BUILD_ROOT/usr/share/dpatch/dpatch/
%{__install} -D dpatch/views/*.py $RPM_BUILD_ROOT/usr/share/dpatch/dpatch/views
cp -rf dpatch/htdocs $RPM_BUILD_ROOT/usr/share/dpatch/dpatch/
cp -rf dpatch/lib $RPM_BUILD_ROOT/usr/share/dpatch/dpatch/
sed -i -e "s/DATA_DIR = os.path.dirname(ROOT_DIR)/DATA_DIR = '\/var\/lib\/dpatch'/" $RPM_BUILD_ROOT/usr/share/dpatch/dpatch/settings.py

%{__install} -d $RPM_BUILD_ROOT/var/lib/dpatch/
%{__install} -d $RPM_BUILD_ROOT/var/lib/dpatch/repo
%{__install} -d $RPM_BUILD_ROOT/var/lib/dpatch/repo/PATCH
%{__install} -d $RPM_BUILD_ROOT/var/lib/dpatch/build
%{__install} -d $RPM_BUILD_ROOT/var/lib/dpatch/pattern
%{__install} -d $RPM_BUILD_ROOT/var/lib/dpatch/pattern/cocci
%{__install} -d $RPM_BUILD_ROOT/var/lib/dpatch/pattern/cocci/patchs
%{__install} -d $RPM_BUILD_ROOT/var/lib/dpatch/pattern/cocci/reports
%{__install} -d $RPM_BUILD_ROOT/var/lib/dpatch/database
%{__install} -D pattern/cocci/patchs/empty.iso $RPM_BUILD_ROOT/var/lib/dpatch/pattern/cocci/patchs/
%{__install} -D pattern/cocci/reports/empty.iso $RPM_BUILD_ROOT/var/lib/dpatch/pattern/cocci/reports/

%{__install} -D -m 644 config/dpatch.wsgi.conf $RPM_BUILD_ROOT/etc/httpd/conf.d/dpatch.conf
%{__install} -D config/dpatch.cron.conf $RPM_BUILD_ROOT/etc/cron.d/dpatch

%clean
rm -rf $RPM_BUILD_ROOT

%files core
%defattr(-,dpatch,dpatch)
%attr(0644,root,root)/etc/cron.d/dpatch
/usr/share/dpatch/bin
/usr/share/dpatch/*.*
/usr/share/dpatch/dpatch/*.*
/usr/share/dpatch/dpatch/lib/
/var/lib/dpatch/repo
/var/lib/dpatch/build
/var/lib/dpatch/pattern
/var/lib/dpatch/database

%files webui
%defattr(-,dpatch,dpatch)
/etc/httpd/conf.d/dpatch.conf
/usr/share/dpatch/dpatch/htdocs
/usr/share/dpatch/dpatch/views

%pre core
/usr/sbin/groupadd -r dpatch &>/dev/null || :
/usr/sbin/useradd -r -s /sbin/nologin -d /usr/share/dpatch -M \
        -c 'Dailypatch User' -s /bin/sh -g dpatch dpatch &>/dev/null || :
if [ -e /var/lib/dpatch/database/sqlite.db ]; then
	cp -rf /var/lib/dpatch/database/sqlite.db /var/lib/dpatch/database/sqlite.db.save
	chown dpatch:dpatch /var/lib/dpatch/database/sqlite.db.save
fi

%post core
/bin/systemctl restart crond.service

%preun core
if [ -e /var/lib/dpatch/database/sqlite.db ]; then
	cp -rf /var/lib/dpatch/database/sqlite.db /var/lib/dpatch/database/sqlite.db.save
	chown dpatch:dpatch /var/lib/dpatch/database/sqlite.db.save
fi

%postun core
/bin/systemctl restart crond.service

%post webui
/bin/systemctl restart httpd.service

%postun webui
/bin/systemctl restart httpd.service

%changelog
* Wed May 14 2012 Wei Yongjun <weiyj.lk@gmail.com>
- Initial build.
