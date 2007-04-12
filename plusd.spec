Summary:	BananaPOS (Point Of Sale) PLU (Price Look UP) Server Daemon
Name:		plusd
Version:	2.0.0
Release:	%mkrel 0.beta3.3
License:	GPL
Group:		System/Servers
URL:		http://www.bananahead.com
Source0:	ftp://bananahead.com/pub/bhpos2/stable/%{name}-%{version}.tar.bz2
Source1:	db.tar.bz2
Source2:	plusd.init.bz2
Source3:	plucache.tar.bz2
Source4:	reconcile_stock_mysql.pl.bz2
Patch0:		plusd-2.0.0-mdv_conf.diff
Patch1:		plusd-2.0.0-plusd_user.diff
Patch2:		plusd-2.0.0-mdv_conf_1.diff
Patch3:		plusd-2.0.0-mdv_conf_2.diff
Patch4:		plusd-2.0.0-64bit.diff
Patch5:		plusd-2.0.0-lib64.diff
Requires(post): rpm-helper
Requires(preun): rpm-helper
Requires(pre): rpm-helper
Requires(postun): rpm-helper
BuildRequires:	libbhpos_commonlibs-devel >= 2.0.0
BuildRequires:	libbhpos_hwlib-devel >= 2.0.0
BuildRequires:	libbhpos_mflibs-devel >= 2.0.0
BuildRequires:	libbhpos_serverlibs-devel >= 2.0.0
Requires:	bhpos_base >= 2.0.0
BuildRequires:	bhpos_base-devel >= 2.0.0
BuildRequires:	gtkmm2.4
BuildRequires:	gtkmm2.4-devel
BuildRequires:	intltool
BuildRequires:	libtool >= 1.5
BuildRequires:	libxml2 >= 2.5.8
BuildRequires:	libusb-devel >= 0.1.8
BuildRequires:	libxml++-devel >= 2.6
BuildRequires:	automake1.7
BuildRequires:	autoconf2.5
BuildRequires:	pkgconfig
BuildRequires:	MySQL-devel
BuildRequires:	openssl-devel
BuildRoot:	%{_tmppath}/%{name}-%{version}

%description
BananaPOS is a point of sale system aimed at the Linux operating
system. This package contains the BananaPOS server dameon.

%package	devel
Summary:	Development files for plusd
Group:		Development/C
Requires:	libtool >= 1.5
Requires:	bhpos_base >= 2.0.0
Requires:	bhpos_base-devel >= 2.0.0
Requires:	libbhpos_commonlibs-devel >= 2.0.0
Requires:	libbhpos_hwlib-devel >= 2.0.0
Requires:	libbhpos_mflibs-devel >= 2.0.0
Requires:	libbhpos_serverlibs-devel >= 2.0.0
Requires:	pkgconfig
Requires:	MySQL-devel
Requires:	openssl-devel

%description	devel
The plusd devel package contains headers required for developing
server plug-ins.

%prep

%setup -q -n %{name}-%{version} -a1
%patch0 -p0
%patch1 -p0
%patch2 -p0
%patch3 -p0
%patch4 -p0
%patch5 -p0

bzcat %{SOURCE2} > plusd.init
tar -jxf %{SOURCE3}
bzcat %{SOURCE4} > reconcile_stock_mysql.pl

# lib64 fixes
perl -pi -e "s|/usr/lib|%{_libdir}|g" scripts/plusd.conf

chmod 644 db/*

%build
export WANT_AUTOCONF_2_5=1
#rm -f configure
#libtoolize --copy --force; aclocal-1.7; autoheader; automake-1.7 --add-missing --copy --gnu; autoconf

sh ./autogen.sh

export DB_MYSQL="1"
export DB_USE_MYSQL_FALSE="#"
export DB_USE_MYSQL_TRUE=""
export MYSQL_CFLAGS="`%{_bindir}/mysql_config --cflags`"
export MYSQL_CONFIG="%{_bindir}/mysql_config"
export MYSQL_LIBS="`%{_bindir}/mysql_config --libs` -lbhmysql"
export MYSQL_MIN_VERSION="4.1.10"
export MYSQL_PREFIX="%{_prefix}"

%configure2_5x \
    --with-mysql=%{_prefix}

# quite borked..., make you go bananas...
echo "#define DB_USE_MYSQL 1" >> config.h.in
echo "#define DB_USE_MYSQL 1" >> config.h

%make

%install
[ "%{buildroot}" != "/" ] && rm -rf %{buildroot}

# don't fiddle with the initscript!
export DONT_GPRINTIFY=1

install -d %{buildroot}%{_initrddir}
install -d %{buildroot}%{_sysconfdir}/logrotate.d
install -d %{buildroot}%{_libdir}/bhpos2.0/modules
install -d %{buildroot}%{_datadir}/bhpos2.0/scripts
install -d %{buildroot}/var/run/plusd
install -d %{buildroot}/var/log/plusd

%makeinstall_std

install -m0755 plusd.init %{buildroot}%{_initrddir}/plusd
install -m0755 plucacheall_mysql.pl %{buildroot}%{_datadir}/bhpos2.0/scripts/plucacheall.pl
install -m0755 reconcile_stock_mysql.pl %{buildroot}%{_datadir}/bhpos2.0/scripts/reconcile_stock.pl

# cleanup
rm -f %{buildroot}/var/run/plusd/plusd.log
echo "#" > %{buildroot}/var/log/plusd/plusd.log

# install log rotation stuff
cat > %{buildroot}%{_sysconfdir}/logrotate.d/plusd << EOF
/var/log/plusd/plusd.log {
    rotate 5
    monthly
    missingok
    notifempty
    nocompress
    prerotate
	%{_initrddir}/plusd restart > /dev/null 2>&1
    endscript
    postrotate
        %{_initrddir}/plusd restart > /dev/null 2>&1
    endscript
}
EOF

%pre
%_pre_useradd plusd /var/log/plusd /bin/sh

%post
%_post_service plusd
%create_ghostfile /var/log/plusd/plusd.log plusd plusd 644

%preun
%_preun_service plusd

%postun
%_postun_userdel plusd

%clean
[ "%{buildroot}" != "/" ] && rm -rf %{buildroot}

%files
%defattr(-,root,root)
%doc ChangeLog NEWS README db
%attr(0755,root,root) %{_initrddir}/plusd
%attr(0644,root,root) %config(noreplace) %{_sysconfdir}/plusd.conf
%attr(0644,root,root) %config(noreplace) %{_sysconfdir}/logrotate.d/plusd
%attr(0755,root,root) %{_sbindir}/plusd
%attr(0755,plusd,plusd) %dir /var/run/plusd
%attr(0755,plusd,plusd) %dir /var/log/plusd
%attr(0644,plusd,plusd) %ghost /var/log/plusd/plusd.log
%attr(0755,root,root) %dir %{_libdir}/bhpos2.0/modules
%attr(0755,root,root) %dir %{_datadir}/bhpos2.0/scripts
%attr(0755,root,root) %{_datadir}/bhpos2.0/scripts/*.pl

%files devel
%defattr(-, root, root)  
%dir %{_includedir}/bhpos2.0/plus
%{_includedir}/bhpos2.0/plus/*.h
%{_libdir}/pkgconfig/plusd-2.0.pc


