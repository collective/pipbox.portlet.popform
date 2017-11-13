from setuptools import setup, find_packages

version = '1.1'

setup(name='pipbox.portlet.popform',
      version=version,
      description="Timed PloneFormGen form popup configured via portlet",
      long_description=open("README.txt").read() + "\n" +
                       open("CHANGES.txt").read(),
      classifiers=[
        "Framework :: Plone",
        "Programming Language :: Python",
        ],
      keywords='pipbox',
      author='Steve McMahon',
      author_email='plone-developers@lists.sourceforge.net',
      url='http://plone.org/products/pipbox.portlet.popform',
      license='GPL',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['pipbox', 'pipbox.portlet'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'setuptools',
          'Products.PloneFormGen>=1.5.5',
          'plone.app.jquerytools',
      ],
      entry_points="""
      # -*- Entry points: -*-

      [z3c.autoinclude.plugin]
      target = plone
      """,
      )
