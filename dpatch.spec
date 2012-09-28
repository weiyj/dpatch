%define debug_package %{nil}

Summary: Automated kernel patch generate engine
Name: dpatch
Version: 0.5
Release: 0%{?dist}
License: GPLv2
Group: System Environment/Base
URL: http://dpatch.org/
Source0: %{name}-%{version}.tar.bz2
BuildRoot: %{_tmppath}/%{name}-%{version}-%{release}-root
Requires: httpd mod_wsgi
Requires: git git-email
Requires: Django
Requires: coccinelle
Requires: gcc make
BuildArch: noarch
ExcludeArch: ppc64 s390 s390x

%description
Automated kernel patch generate engine

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
sed -i -e "s/DATA_DIR = os.path.dirname(ROOT_DIR)/DATA_DIR = '\/var\/lib\/dpatch'/" $RPM_BUILD_ROOT/usr/share/dpatch/dpatch/settings.py

%{__install} -d $RPM_BUILD_ROOT/var/lib/dpatch/
%{__install} -d $RPM_BUILD_ROOT/var/lib/dpatch/repo
%{__install} -d $RPM_BUILD_ROOT/var/lib/dpatch/repo/PATCH
%{__install} -d $RPM_BUILD_ROOT/var/lib/dpatch/build
%{__install} -d $RPM_BUILD_ROOT/var/lib/dpatch/pattern
%{__install} -d $RPM_BUILD_ROOT/var/lib/dpatch/pattern/cocci
%{__install} -d $RPM_BUILD_ROOT/var/lib/dpatch/pattern/cocci/report
%{__install} -d $RPM_BUILD_ROOT/var/lib/dpatch/database
#%{__install} -m 644 -D database/*.db $RPM_BUILD_ROOT/var/lib/dpatch/database/

%{__install} -D -m 644 config/dpatch.conf $RPM_BUILD_ROOT/etc/httpd/conf.d/dpatch.conf
%{__install} -D config/dpatch.sh $RPM_BUILD_ROOT/etc/cron.d/dpatch

%clean
rm -rf $RPM_BUILD_ROOT

%files
%defattr(-,dpatch,dpatch)
%attr(0644,root,root)/etc/cron.d/dpatch
/etc/httpd/conf.d/dpatch.conf
/usr/share/dpatch
/var/lib/dpatch/repo
/var/lib/dpatch/build
/var/lib/dpatch/pattern
/var/lib/dpatch/database

%pre
/usr/sbin/groupadd -r dpatch &>/dev/null || :
/usr/sbin/useradd -r -s /sbin/nologin -d /usr/share/dpatch -M \
        -c 'Dailypatch User' -s /bin/sh -g dpatch dpatch &>/dev/null || :

%post
/bin/systemctl restart httpd.service
/bin/systemctl restart crond.service

%preun

%postun
/bin/systemctl restart httpd.service
/bin/systemctl restart crond.service

%changelog
* Wed May 14 2012 Wei Yongjun <weiyj.lk@gmail.com>
- Initial build.
