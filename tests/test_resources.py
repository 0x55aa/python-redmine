from tests import unittest, mock, Redmine, URL
from redmine.resultsets import ResourceSet

responses = {
    'project': {
        'get': {'project': {'name': 'Foo', 'id': 1}},
        'all': {'projects': [{'name': 'Foo', 'id': 1}, {'name': 'Bar', 'id': 2}]},
    },
    'issue': {
        'get': {'issue': {'subject': 'Foo', 'id': 1}},
        'all': {'issues': [{'subject': 'Foo', 'id': 1}, {'subject': 'Bar', 'id': 2}]},
        'filter': {'issues': [{'subject': 'Foo', 'id': 1}, {'subject': 'Bar', 'id': 2}]},
    },
    'time_entry': {
        'get': {'time_entry': {'hours': 2, 'id': 1}},
        'all': {'time_entries': [{'hours': 3, 'id': 1}, {'hours': 4, 'id': 2}]},
        'filter': {'time_entries': [{'hours': 3, 'id': 1}, {'hours': 4, 'id': 2}]},
    },
    'enumeration': {
        'filter': {'time_entry_activities': [{'name': 'Foo', 'id': 1}, {'name': 'Bar', 'id': 2}]},
    },
    'attachment': {
        'get': {'attachment': {'filename': 'foo.jpg', 'id': 1}},
    },
    'wiki_page': {
        'get': {'wiki_page': {'title': 'Foo', 'version': 1}},
        'filter': {'wiki_pages': [{'title': 'Foo', 'version': 1}, {'title': 'Bar', 'version': 2}]},
    },
    'project_membership': {
        'get': {'membership': {'id': 1}},
        'filter': {'memberships': [{'id': 1}, {'id': 2}]},
    },
    'issue_category': {
        'get': {'issue_category': {'id': 1, 'name': 'Foo'}},
        'filter': {'issue_categories': [{'id': 1, 'name': 'Foo'}, {'id': 2, 'name': 'Bar'}]},
    },
    'issue_relation': {
        'get': {'relation': {'id': 1}},
        'filter': {'relations': [{'id': 1}, {'id': 2}]},
    },
    'version': {
        'get': {'version': {'id': 1, 'name': 'Foo'}},
        'filter': {'versions': [{'id': 1, 'name': 'Foo'}, {'id': 2, 'name': 'Bar'}]},
    },
    'user': {
        'get': {'user': {'firstname': 'John', 'lastname': 'Smith', 'id': 1}},
        'all': {'users': [{'firstname': 'John', 'id': 1}, {'firstname': 'Jack', 'id': 2}]},
        'filter': {'users': [{'firstname': 'John', 'id': 1}, {'firstname': 'Jack', 'id': 2}]},
    },
    'group': {
        'get': {'group': {'name': 'Foo', 'id': 1}},
        'all': {'groups': [{'name': 'Foo', 'id': 1}, {'name': 'Bar', 'id': 2}]},
    },
    'role': {
        'get': {'role': {'name': 'Foo', 'id': 1}},
        'all': {'roles': [{'name': 'Foo', 'id': 1}, {'name': 'Bar', 'id': 2}]},
    },
    'news': {
        'all': {'news': [{'title': 'Foo', 'id': 1}, {'title': 'Bar', 'id': 2}]},
        'filter': {'news': [{'title': 'Foo', 'id': 1}, {'title': 'Bar', 'id': 2}]},
    },
    'issue_status': {
        'all': {'issue_statuses': [{'name': 'Foo', 'id': 1}, {'name': 'Bar', 'id': 2}]},
    },
    'tracker': {
        'all': {'trackers': [{'name': 'Foo', 'id': 1}, {'name': 'Bar', 'id': 2}]},
    },
    'query': {
        'all': {'queries': [{'name': 'Foo', 'id': 1}, {'name': 'Bar', 'id': 2}]},
    },
    'custom_field': {
        'all': {'custom_fields': [{'name': 'Foo', 'id': 1}, {'name': 'Bar', 'id': 2}]},
    },
}


class TestResources(unittest.TestCase):
    def setUp(self):
        self.url = URL
        self.redmine = Redmine(self.url)
        self.response = mock.Mock(status_code=200)
        patcher_get = mock.patch('requests.get', return_value=self.response)
        patcher_post = mock.patch('requests.post', return_value=self.response)
        patcher_put = mock.patch('requests.put', return_value=self.response)
        patcher_delete = mock.patch('requests.delete', return_value=self.response)
        patcher_get.start()
        patcher_post.start()
        patcher_put.start()
        patcher_delete.start()
        self.addCleanup(patcher_get.stop)
        self.addCleanup(patcher_post.stop)
        self.addCleanup(patcher_put.stop)
        self.addCleanup(patcher_delete.stop)

    def test_supports_dictionary_like_attribute_retrieval(self):
        self.response.json.return_value = responses['project']['get']
        project = self.redmine.project.get(1)
        self.assertEqual(project['id'], 1)
        self.assertEqual(project['name'], 'Foo')

    def test_supports_url_retrieval(self):
        self.response.json.return_value = responses['project']['get']
        self.assertEqual(self.redmine.project.get(1).url, '{0}/projects/1'.format(self.url))

    def test_supports_internal_id(self):
        self.response.json.return_value = responses['project']['get']
        self.assertEqual(self.redmine.project.get(1).internal_id, 1)

    def test_supports_setting_of_attributes(self):
        project = self.redmine.project.new()
        project.name = 'Foo'
        project.description = 'Bar'
        self.assertEqual(project.name, 'Foo')
        self.assertEqual(project.description, 'Bar')

    def test_supports_setting_of_attributes_via_dict(self):
        project = self.redmine.project.new()
        project['name'] = 'Foo'
        project['description'] = 'Bar'
        self.assertEqual(project.name, 'Foo')
        self.assertEqual(project.description, 'Bar')

    def test_setting_readonly_attrs_raises_exception(self):
        from redmine.exceptions import ReadonlyAttrError
        with self.assertRaises(ReadonlyAttrError):
            project = self.redmine.project.new()
            project.id = 1

    def test_control_raising_of_resource_attr_exception(self):
        from redmine.exceptions import ResourceAttrError
        self.response.json.return_value = responses['project']['get']
        self.redmine.raise_attr_exception = False
        self.assertEqual(self.redmine.project.get(1).foo, None)
        self.redmine.raise_attr_exception = ('Project',)
        self.assertRaises(ResourceAttrError, lambda: self.redmine.project.get(1).foo)
        self.redmine.raise_attr_exception = True
        self.assertRaises(ResourceAttrError, lambda: self.redmine.project.get(1).foo)

    def test_saving_new_resource_creates_it(self):
        self.response.status_code = 201
        self.response.json.return_value = responses['project']['get']
        project = self.redmine.project.new()
        project.name = 'Foo'
        self.assertEqual(project.save(), True)
        self.assertEqual(project.id, 1)

    def test_saving_existing_resource_updates_it(self):
        self.response.json.return_value = responses['project']['get']
        project = self.redmine.project.get(1)
        project.name = 'Bar'
        self.assertEqual(project.save(), True)
        self.response.json.return_value = {'project': {'id': 1, 'name': 'Bar'}}
        project = project.refresh()
        self.assertEqual(project.name, 'Bar')

    def test_custom_int(self):
        self.response.json.return_value = responses['project']['get']
        self.assertEqual(int(self.redmine.project.get(1)), 1)

    def test_custom_str(self):
        self.response.json.return_value = responses['project']['get']
        self.assertEqual(str(self.redmine.project.get(1)), 'Foo')

    def test_custom_repr(self):
        self.response.json.return_value = responses['project']['get']
        self.assertEqual(repr(self.redmine.project.get(1)), '<redmine.resources.Project #1 "Foo">')

    def test_can_refresh_itself(self):
        self.response.json.return_value = responses['project']['get']
        project = self.redmine.project.get(1)
        self.assertEqual(project.id, 1)
        self.assertEqual(project.name, 'Foo')
        self.response.json.return_value = {'project': {'id': 2, 'name': 'Bar'}}
        project = project.refresh()
        self.assertEqual(project.id, 2)
        self.assertEqual(project.name, 'Bar')

    def test_resource_dict_is_converted_to_resource_object(self):
        self.response.json.return_value = responses['issue']['get']
        issue = self.redmine.issue.get(1)
        issue.attributes['author'] = {'id': 1, 'name': 'John Smith'}
        self.assertEqual(repr(issue.author), '<redmine.resources.User #1 "John Smith">')

    def test_resource_list_of_dicts_is_converted_to_resource_set(self):
        self.response.json.return_value = responses['issue']['get']
        issue = self.redmine.issue.get(1)
        issue.attributes['custom_fields'] = [{'id': 1, 'name': 'Foo'}, {'id': 2, 'name': 'Bar'}]
        self.assertEqual(
            repr(issue.custom_fields),
            '<redmine.resultsets.ResourceSet object with CustomField resources>'
        )

    def test_dir_returns_resource_attributes(self):
        self.response.json.return_value = responses['issue']['get']
        attributes = dir(self.redmine.issue.get(1))
        self.assertIn('id', attributes)
        self.assertIn('subject', attributes)
        self.assertIn('relations', attributes)
        self.assertIn('time_entries', attributes)

    def test_supports_iteration(self):
        self.response.json.return_value = responses['project']['get']
        project = list(self.redmine.project.get(1))
        self.assertIn(('name', 'Foo'), project)
        self.assertIn(('id', 1), project)

    def test_setting_custom_field_raises_exception_if_not_list_of_dicts(self):
        from redmine.exceptions import CustomFieldValueError
        response = {'project': {'name': 'Foo', 'id': 1, 'custom_fields': [{'id': 1}]}}
        self.response.json.return_value = response
        project = self.redmine.project.get(1)
        with self.assertRaises(CustomFieldValueError):
            project.custom_fields = 'foo'

    def test_project_version(self):
        self.assertEqual(self.redmine.project.resource_class.redmine_version, '1.0')

    def test_project_get(self):
        self.response.json.return_value = responses['project']['get']
        project = self.redmine.project.get(1)
        self.assertEqual(project.id, 1)
        self.assertEqual(project.name, 'Foo')

    def test_project_all(self):
        self.response.json.return_value = responses['project']['all']
        projects = self.redmine.project.all()
        self.assertEqual(projects[0].id, 1)
        self.assertEqual(projects[0].name, 'Foo')
        self.assertEqual(projects[1].id, 2)
        self.assertEqual(projects[1].name, 'Bar')

    def test_project_create(self):
        self.response.status_code = 201
        self.response.json.return_value = responses['project']['get']
        project = self.redmine.project.create(name='Foo', identifier='foo')
        self.assertEqual(project.id, 1)
        self.assertEqual(project.name, 'Foo')

    def test_project_delete(self):
        self.response.content = ''
        self.assertEqual(self.redmine.project.delete(1), True)

    def test_project_update(self):
        response = {'project': {'name': 'Foo', 'id': 1, 'custom_fields': [{'id': 1, 'value': 'foo'}]}}
        self.response.json.return_value = response
        project = self.redmine.project.get(1)
        project.homepage = 'http://foo.bar'
        project.parent_id = 3
        project.custom_fields = [{'id': 1, 'value': 'bar'}]
        self.assertEqual(project.save(), True)
        self.assertEqual(project.custom_fields[0].value, 'bar')

    def test_project_relations(self):
        self.response.json.return_value = responses['project']['get']
        project = self.redmine.project.get(1)
        self.assertIsInstance(project.wiki_pages, ResourceSet)
        self.assertIsInstance(project.memberships, ResourceSet)
        self.assertIsInstance(project.issue_categories, ResourceSet)
        self.assertIsInstance(project.versions, ResourceSet)
        self.assertIsInstance(project.news, ResourceSet)
        self.assertIsInstance(project.issues, ResourceSet)

    def test_project_includes(self):
        response_includes = responses['project']['get']
        self.response.json.return_value = response_includes
        project = self.redmine.project.get(1)
        response_includes['project'].update(responses['issue_category']['filter'])
        self.response.json.return_value = response_includes
        self.assertIsInstance(project.issue_categories, ResourceSet)
        response_includes['project'].update(responses['tracker']['all'])
        self.response.json.return_value = response_includes
        self.assertIsInstance(project.trackers, ResourceSet)

    def test_issue_version(self):
        self.assertEqual(self.redmine.issue.resource_class.redmine_version, '1.0')

    def test_issue_get(self):
        self.response.json.return_value = responses['issue']['get']
        issue = self.redmine.issue.get(1)
        self.assertEqual(issue.id, 1)
        self.assertEqual(issue.subject, 'Foo')

    def test_issue_all(self):
        self.response.json.return_value = responses['issue']['all']
        issues = self.redmine.issue.all()
        self.assertEqual(issues[0].id, 1)
        self.assertEqual(issues[0].subject, 'Foo')
        self.assertEqual(issues[1].id, 2)
        self.assertEqual(issues[1].subject, 'Bar')

    def test_issue_filter(self):
        self.response.json.return_value = responses['issue']['filter']
        issues = self.redmine.issue.filter(project_id=1)
        self.assertEqual(issues[0].id, 1)
        self.assertEqual(issues[0].subject, 'Foo')
        self.assertEqual(issues[1].id, 2)
        self.assertEqual(issues[1].subject, 'Bar')

    def test_issue_create(self):
        self.response.status_code = 201
        self.response.json.return_value = responses['issue']['get']
        issue = self.redmine.issue.create(project_id='bar', subject='Foo')
        self.assertEqual(issue.id, 1)
        self.assertEqual(issue.subject, 'Foo')

    def test_issue_delete(self):
        self.response.content = ''
        self.assertEqual(self.redmine.issue.delete(1), True)

    def test_issue_update(self):
        response = {'issue': {'name': 'Foo', 'id': 1, 'custom_fields': [{'id': 1, 'value': 'foo'}]}}
        self.response.json.return_value = response
        issue = self.redmine.issue.get(1)
        issue.subject = 'Foo'
        issue.description = 'foobar'
        issue.custom_fields = [{'id': 1, 'value': 'bar'}]
        self.assertEqual(issue.save(), True)
        self.assertEqual(issue.custom_fields[0].value, 'bar')

    def test_issue_relations(self):
        self.response.json.return_value = responses['issue']['get']
        issue = self.redmine.issue.get(1)
        self.assertIsInstance(issue.relations, ResourceSet)
        self.assertIsInstance(issue.time_entries, ResourceSet)

    def test_issue_includes(self):
        response_includes = responses['issue']['get']
        self.response.json.return_value = response_includes
        issue = self.redmine.issue.get(1)
        response_includes['issue']['children'] = responses['issue']['all']['issues']
        self.response.json.return_value = response_includes
        self.assertIsInstance(issue.children, ResourceSet)
        response_includes['issue']['attachments'] = responses['attachment']['get']
        self.response.json.return_value = response_includes
        self.assertIsInstance(issue.attachments, ResourceSet)
        response_includes['issue']['relations'] = responses['issue_relation']['get']['relation']
        self.response.json.return_value = response_includes
        self.assertIsInstance(issue.relations, ResourceSet)
        response_includes['issue']['journals'] = [{'id': 1}, {'id': 2}]
        self.response.json.return_value = response_includes
        self.assertIsInstance(issue.journals, ResourceSet)
        response_includes['issue']['watchers'] = responses['user']['all']['users']
        self.response.json.return_value = response_includes
        self.assertIsInstance(issue.watchers, ResourceSet)

    def test_issue_add_watcher_raises_exception_if_wrong_version(self):
        from redmine.exceptions import ResourceVersionMismatchError
        self.response.json.return_value = responses['issue']['get']
        self.redmine.ver = '2.2.0'
        issue = self.redmine.issue.get(1)
        self.response.content = ''
        self.assertRaises(ResourceVersionMismatchError, lambda: issue.watcher.add(1))

    def test_issue_add_watcher(self):
        self.response.json.return_value = responses['issue']['get']
        issue = self.redmine.issue.get(1)
        self.response.content = ''
        self.assertEqual(issue.watcher.add(1), True)

    def test_issue_remove_watcher(self):
        self.response.json.return_value = responses['issue']['get']
        issue = self.redmine.issue.get(1)
        self.response.content = ''
        self.assertEqual(issue.watcher.remove(1), True)

    def test_issue_custom_repr(self):
        self.response.json.return_value = responses['issue']['get']
        self.assertEqual(repr(self.redmine.issue.get(1)), '<redmine.resources.Issue #1 "Foo">')

    def test_issue_custom_repr_without_subject(self):
        self.response.json.return_value = responses['issue']['get']
        issue = self.redmine.issue.get(1)
        del issue['attributes']['subject']
        self.assertEqual(repr(issue), '<redmine.resources.Issue #1>')

    def test_issue_custom_str(self):
        self.response.json.return_value = responses['issue']['get']
        self.assertEqual(str(self.redmine.issue.get(1)), 'Foo')

    def test_issue_custom_str_without_subject(self):
        self.response.json.return_value = responses['issue']['get']
        issue = self.redmine.issue.get(1)
        del issue['attributes']['subject']
        self.assertEqual(str(issue), '1')

    def test_issue_journals(self):
        self.response.json.return_value = responses['issue']['get']
        issue = self.redmine.issue.get(1)
        issue.attributes['journals'] = [{'id': 1}]
        self.assertEqual(str(issue.journals[0]), '1')
        self.assertEqual(repr(issue.journals[0]), '<redmine.resources.IssueJournal #1>')

    def test_issue_version_can_be_retrieved_via_version_attribute(self):
        from redmine.resources import Version
        response = {'issue': {'subject': 'Foo', 'id': 1, 'fixed_version': {'id': 1, 'name': 'Foo'}}}
        self.response.json.return_value = response
        issue = self.redmine.issue.get(1)
        self.assertIsInstance(issue.version, Version)

    def test_issue_version_can_be_set_via_version_attribute(self):
        self.response.json.return_value = responses['issue']['get']
        issue = self.redmine.issue.get(1)
        issue.version_id = 1
        self.assertEqual(issue.fixed_version.id, 1)

    def test_time_entry_version(self):
        self.assertEqual(self.redmine.time_entry.resource_class.redmine_version, '1.1')

    def test_time_entry_get(self):
        self.response.json.return_value = responses['time_entry']['get']
        time_entry = self.redmine.time_entry.get(1)
        self.assertEqual(time_entry.id, 1)
        self.assertEqual(time_entry.hours, 2)

    def test_time_entry_all(self):
        self.response.json.return_value = responses['time_entry']['all']
        time_entries = self.redmine.time_entry.all()
        self.assertEqual(time_entries[0].id, 1)
        self.assertEqual(time_entries[0].hours, 3)
        self.assertEqual(time_entries[1].id, 2)
        self.assertEqual(time_entries[1].hours, 4)

    def test_time_entry_filter(self):
        self.response.json.return_value = responses['time_entry']['filter']
        time_entries = self.redmine.time_entry.filter(issue_id=1)
        self.assertEqual(time_entries[0].id, 1)
        self.assertEqual(time_entries[0].hours, 3)
        self.assertEqual(time_entries[1].id, 2)
        self.assertEqual(time_entries[1].hours, 4)

    def test_time_entry_create(self):
        self.response.status_code = 201
        self.response.json.return_value = responses['time_entry']['get']
        time_entry = self.redmine.time_entry.create(issue_id=1, hours=2)
        self.assertEqual(time_entry.id, 1)
        self.assertEqual(time_entry.hours, 2)

    def test_time_entry_delete(self):
        self.response.content = ''
        self.assertEqual(self.redmine.time_entry.delete(1), True)

    def test_time_entry_update(self):
        response = {'time_entry': {'hours': 2, 'id': 1, 'issue': {'id': 1}, 'activity': {'id': 1}}}
        self.response.json.return_value = response
        time_entry = self.redmine.time_entry.get(1)
        time_entry.hours = 3
        time_entry.issue_id = 2
        time_entry.activity_id = 2
        self.assertEqual(time_entry.save(), True)

    def test_time_entry_translate_params(self):
        manager = self.redmine.time_entry
        manager.filter(from_date='2013-12-30', to_date='2013-12-31')
        self.assertIn('from', manager.params)
        self.assertIn('to', manager.params)

    def test_time_entry_custom_str(self):
        self.response.json.return_value = responses['time_entry']['get']
        self.assertEqual(str(self.redmine.time_entry.get(1)), '1')

    def test_time_entry_custom_repr(self):
        self.response.json.return_value = responses['time_entry']['get']
        self.assertEqual(repr(self.redmine.time_entry.get(1)), '<redmine.resources.TimeEntry #1>')

    def test_enumeration_version(self):
        self.assertEqual(self.redmine.enumeration.resource_class.redmine_version, '2.2')

    def test_enumeration_filter(self):
        self.response.json.return_value = responses['enumeration']['filter']
        enumerations = self.redmine.enumeration.filter(resource='time_entry_activities')
        self.assertEqual(enumerations[0].id, 1)
        self.assertEqual(enumerations[0].name, 'Foo')
        self.assertEqual(enumerations[1].id, 2)
        self.assertEqual(enumerations[1].name, 'Bar')

    def test_attachment_version(self):
        self.assertEqual(self.redmine.attachment.resource_class.redmine_version, '1.3')

    def test_attachment_get(self):
        self.response.json.return_value = responses['attachment']['get']
        attachment = self.redmine.attachment.get(1)
        self.assertEqual(attachment.id, 1)
        self.assertEqual(attachment.filename, 'foo.jpg')

    def test_attachment_custom_str(self):
        self.response.json.return_value = responses['attachment']['get']
        self.assertEqual(str(self.redmine.attachment.get(1)), 'foo.jpg')

    def test_attachment_custom_repr(self):
        self.response.json.return_value = responses['attachment']['get']
        self.assertEqual(repr(self.redmine.attachment.get(1)), '<redmine.resources.Attachment #1 "foo.jpg">')

    def test_wiki_page_version(self):
        self.assertEqual(self.redmine.wiki_page.resource_class.redmine_version, '2.2')

    def test_wiki_page_get(self):
        self.response.json.return_value = responses['wiki_page']['get']
        wiki_page = self.redmine.wiki_page.get('Foo', project_id=1)
        self.assertEqual(wiki_page.title, 'Foo')

    def test_wiki_page_filter(self):
        self.response.json.return_value = responses['wiki_page']['filter']
        wiki_pages = self.redmine.wiki_page.filter(project_id=1)
        self.assertEqual(wiki_pages[0].title, 'Foo')
        self.assertEqual(wiki_pages[1].title, 'Bar')

    def test_wiki_page_create(self):
        self.response.status_code = 201
        self.response.json.return_value = responses['wiki_page']['get']
        wiki_page = self.redmine.wiki_page.create(project_id='foo', title='Foo')
        self.assertEqual(wiki_page.title, 'Foo')

    def test_wiki_page_delete(self):
        self.response.content = ''
        self.assertEqual(self.redmine.wiki_page.delete('Foo', project_id=1), True)

    def test_wiki_page_update(self):
        self.response.json.return_value = responses['wiki_page']['get']
        wiki_page = self.redmine.wiki_page.get('Foo', project_id=1)
        wiki_page.text = 'Foo'
        self.assertEqual(wiki_page.save(), True)
        self.assertEqual(wiki_page.version, 2)

    def test_wiki_page_refresh_by_title(self):
        self.response.json.return_value = responses['wiki_page']['get']
        wiki_page = self.redmine.wiki_page.get('title', project_id=1)
        self.assertEqual(wiki_page.title, 'Foo')
        self.response.json.return_value = {'wiki_page': {'title': 'Bar'}}
        wiki_page = wiki_page.refresh()
        self.assertEqual(wiki_page.title, 'Bar')

    def test_wiki_page_supports_internal_id(self):
        self.response.json.return_value = responses['wiki_page']['get']
        self.assertEqual(self.redmine.wiki_page.get('Foo', project_id=1).internal_id, 'Foo')

    def test_wiki_page_custom_int(self):
        self.response.json.return_value = responses['wiki_page']['get']
        print(int(self.redmine.wiki_page.get('Foo', project_id=1)))
        self.assertEqual(int(self.redmine.wiki_page.get('Foo', project_id=1)), 1)

    def test_wiki_page_custom_str(self):
        self.response.json.return_value = responses['wiki_page']['get']
        self.assertEqual(str(self.redmine.wiki_page.get('Foo', project_id=1)), 'Foo')

    def test_wiki_page_custom_repr(self):
        self.response.json.return_value = responses['wiki_page']['get']
        self.assertEqual(repr(self.redmine.wiki_page.get('Foo', project_id=1)), '<redmine.resources.WikiPage "Foo">')

    def test_wiki_page_includes(self):
        response_includes = responses['wiki_page']['get']
        self.response.json.return_value = response_includes
        wiki_page = self.redmine.wiki_page.get('Foo', project_id=1)
        response_includes['wiki_page']['attachments'] = responses['attachment']['get']['attachment']
        self.response.json.return_value = response_includes
        self.assertIsInstance(wiki_page.attachments, ResourceSet)

    def test_project_membership_version(self):
        self.assertEqual(self.redmine.project_membership.resource_class.redmine_version, '1.4')

    def test_project_membership_get(self):
        self.response.json.return_value = responses['project_membership']['get']
        membership = self.redmine.project_membership.get(1)
        self.assertEqual(membership.id, 1)

    def test_project_membership_filter(self):
        self.response.json.return_value = responses['project_membership']['filter']
        memberships = self.redmine.project_membership.filter(project_id=1)
        self.assertEqual(memberships[0].id, 1)
        self.assertEqual(memberships[1].id, 2)

    def test_project_membership_create(self):
        self.response.status_code = 201
        self.response.json.return_value = responses['project_membership']['get']
        membership = self.redmine.project_membership.create(project_id='foo', user_id=1, role_ids=[1, 2])
        self.assertEqual(membership.id, 1)

    def test_project_membership_delete(self):
        self.response.content = ''
        self.assertEqual(self.redmine.project_membership.delete(1), True)

    def test_project_membership_update(self):
        self.response.json.return_value = responses['project_membership']['get']
        membership = self.redmine.project_membership.get(1)
        membership.role_ids = [1, 2]
        self.assertEqual(membership.save(), True)
        self.assertEqual(membership.roles[0].id, 1)
        self.assertEqual(membership.roles[1].id, 2)

    def test_project_membership_custom_str(self):
        self.response.json.return_value = responses['project_membership']['get']
        self.assertEqual(str(self.redmine.project_membership.get(1)), '1')

    def test_project_membership_custom_repr(self):
        self.response.json.return_value = responses['project_membership']['get']
        self.assertEqual(repr(self.redmine.project_membership.get(1)), '<redmine.resources.ProjectMembership #1>')

    def test_issue_category_version(self):
        self.assertEqual(self.redmine.issue_category.resource_class.redmine_version, '1.3')

    def test_issue_category_get(self):
        self.response.json.return_value = responses['issue_category']['get']
        issue_category = self.redmine.issue_category.get(1)
        self.assertEqual(issue_category.id, 1)
        self.assertEqual(issue_category.name, 'Foo')

    def test_issue_category_filter(self):
        self.response.json.return_value = responses['issue_category']['filter']
        categories = self.redmine.issue_category.filter(project_id=1)
        self.assertEqual(categories[0].id, 1)
        self.assertEqual(categories[0].name, 'Foo')
        self.assertEqual(categories[1].id, 2)
        self.assertEqual(categories[1].name, 'Bar')

    def test_issue_category_create(self):
        self.response.status_code = 201
        self.response.json.return_value = responses['issue_category']['get']
        category = self.redmine.issue_category.create(project_id='foo', name='Foo')
        self.assertEqual(category.name, 'Foo')

    def test_issue_category_delete(self):
        self.response.content = ''
        self.assertEqual(self.redmine.issue_category.delete(1), True)

    def test_issue_category_update(self):
        self.response.json.return_value = responses['issue_category']['get']
        category = self.redmine.issue_category.get(1)
        category.name = 'Bar'
        self.assertEqual(category.save(), True)

    def test_issue_relation_version(self):
        self.assertEqual(self.redmine.issue_relation.resource_class.redmine_version, '1.3')

    def test_issue_relation_get(self):
        self.response.json.return_value = responses['issue_relation']['get']
        relation = self.redmine.issue_relation.get(1)
        self.assertEqual(relation.id, 1)

    def test_issue_relation_filter(self):
        self.response.json.return_value = responses['issue_relation']['filter']
        relations = self.redmine.issue_relation.filter(issue_id=1)
        self.assertEqual(relations[0].id, 1)
        self.assertEqual(relations[1].id, 2)

    def test_issue_relation_create(self):
        self.response.status_code = 201
        self.response.json.return_value = responses['issue_relation']['get']
        relation = self.redmine.issue_relation.create(issue_id=1, issue_to_id=2)
        self.assertEqual(relation.id, 1)

    def test_issue_relation_delete(self):
        self.response.content = ''
        self.assertEqual(self.redmine.issue_relation.delete(1), True)

    def test_issue_relation_custom_str(self):
        self.response.json.return_value = responses['issue_relation']['get']
        self.assertEqual(str(self.redmine.issue_relation.get(1)), '1')

    def test_issue_relation_custom_repr(self):
        self.response.json.return_value = responses['issue_relation']['get']
        self.assertEqual(repr(self.redmine.issue_relation.get(1)), '<redmine.resources.IssueRelation #1>')

    def test_version_version(self):
        self.assertEqual(self.redmine.version.resource_class.redmine_version, '1.3')

    def test_version_get(self):
        self.response.json.return_value = responses['version']['get']
        version = self.redmine.version.get(1)
        self.assertEqual(version.id, 1)
        self.assertEqual(version.name, 'Foo')

    def test_version_filter(self):
        self.response.json.return_value = responses['version']['filter']
        versions = self.redmine.version.filter(project_id=1)
        self.assertEqual(versions[0].id, 1)
        self.assertEqual(versions[0].name, 'Foo')
        self.assertEqual(versions[1].id, 2)
        self.assertEqual(versions[1].name, 'Bar')

    def test_version_create(self):
        self.response.status_code = 201
        self.response.json.return_value = responses['version']['get']
        version = self.redmine.version.create(project_id='foo', name='Foo')
        self.assertEqual(version.name, 'Foo')

    def test_version_delete(self):
        self.response.content = ''
        self.assertEqual(self.redmine.version.delete(1), True)

    def test_version_update(self):
        self.response.json.return_value = responses['version']['get']
        version = self.redmine.version.get(1)
        version.name = 'Bar'
        self.assertEqual(version.save(), True)

    def test_version_returns_status_without_conversion(self):
        self.response.json.return_value = {'version': {'id': 1, 'name': 'Foo', 'status': 'foo'}}
        version = self.redmine.version.get(1)
        self.assertEqual(version.status, 'foo')

    def test_user_version(self):
        self.assertEqual(self.redmine.user.resource_class.redmine_version, '1.1')

    def test_user_get(self):
        self.response.json.return_value = responses['user']['get']
        user = self.redmine.user.get(1)
        self.assertEqual(user.id, 1)
        self.assertEqual(user.firstname, 'John')

    def test_user_all(self):
        self.response.json.return_value = responses['user']['all']
        users = self.redmine.user.all()
        self.assertEqual(users[0].id, 1)
        self.assertEqual(users[0].firstname, 'John')
        self.assertEqual(users[1].id, 2)
        self.assertEqual(users[1].firstname, 'Jack')

    def test_user_filter(self):
        self.response.json.return_value = responses['user']['filter']
        users = self.redmine.user.filter(status_id=2)
        self.assertEqual(users[0].id, 1)
        self.assertEqual(users[0].firstname, 'John')
        self.assertEqual(users[1].id, 2)
        self.assertEqual(users[1].firstname, 'Jack')

    def test_user_create(self):
        self.response.status_code = 201
        self.response.json.return_value = responses['user']['get']
        user = self.redmine.user.create(firstname='John', lastname='Smith')
        self.assertEqual(user.firstname, 'John')
        self.assertEqual(user.lastname, 'Smith')

    def test_user_delete(self):
        self.response.content = ''
        self.assertEqual(self.redmine.user.delete(1), True)

    def test_user_update(self):
        self.response.json.return_value = responses['user']['get']
        user = self.redmine.user.get(1)
        user.lastname = 'Foo'
        user.firstname = 'Bar'
        self.assertEqual(user.save(), True)

    def test_user_custom_str(self):
        self.response.json.return_value = responses['user']['get']
        self.assertEqual(str(self.redmine.user.get(1)), 'John Smith')

    def test_user_custom_repr(self):
        self.response.json.return_value = responses['user']['get']
        self.assertEqual(repr(self.redmine.user.get(1)), '<redmine.resources.User #1 "John Smith">')

    def test_user_includes(self):
        response_includes = responses['user']['get']
        self.response.json.return_value = response_includes
        user = self.redmine.user.get(1)
        response_includes['user']['memberships'] = responses['project_membership']['filter']['memberships']
        self.response.json.return_value = response_includes
        self.assertIsInstance(user.memberships, ResourceSet)
        response_includes['user']['groups'] = responses['group']['all']['groups']
        self.response.json.return_value = response_includes
        self.assertIsInstance(user.groups, ResourceSet)

    def test_group_version(self):
        self.assertEqual(self.redmine.group.resource_class.redmine_version, '2.1')

    def test_group_get(self):
        self.response.json.return_value = responses['group']['get']
        group = self.redmine.group.get(1)
        self.assertEqual(group.id, 1)
        self.assertEqual(group.name, 'Foo')

    def test_group_all(self):
        self.response.json.return_value = responses['group']['all']
        groups = self.redmine.group.all()
        self.assertEqual(groups[0].id, 1)
        self.assertEqual(groups[0].name, 'Foo')
        self.assertEqual(groups[1].id, 2)
        self.assertEqual(groups[1].name, 'Bar')

    def test_group_create(self):
        self.response.status_code = 201
        self.response.json.return_value = responses['group']['get']
        group = self.redmine.group.create(name='Foo')
        self.assertEqual(group.name, 'Foo')

    def test_group_delete(self):
        self.response.content = ''
        self.assertEqual(self.redmine.group.delete(1), True)

    def test_group_update(self):
        self.response.json.return_value = responses['group']['get']
        group = self.redmine.group.get(1)
        group.name = 'Bar'
        self.assertEqual(group.save(), True)

    def test_group_includes(self):
        response_includes = responses['group']['get']
        self.response.json.return_value = response_includes
        group = self.redmine.group.get(1)
        response_includes['group']['memberships'] = responses['project_membership']['filter']['memberships']
        self.response.json.return_value = response_includes
        self.assertIsInstance(group.memberships, ResourceSet)
        response_includes['group']['users'] = responses['user']['all']['users']
        self.response.json.return_value = response_includes
        self.assertIsInstance(group.users, ResourceSet)

    def test_group_add_user(self):
        self.response.json.return_value = responses['group']['get']
        group = self.redmine.group.get(1)
        self.response.content = ''
        self.assertEqual(group.user.add(1), True)

    def test_group_remove_user(self):
        self.response.json.return_value = responses['group']['get']
        group = self.redmine.group.get(1)
        self.response.content = ''
        self.assertEqual(group.user.remove(1), True)

    def test_role_version(self):
        self.assertEqual(self.redmine.role.resource_class.redmine_version, '1.4')

    def test_role_get(self):
        self.response.json.return_value = responses['role']['get']
        role = self.redmine.role.get(1)
        self.assertEqual(role.id, 1)
        self.assertEqual(role.name, 'Foo')

    def test_role_all(self):
        self.response.json.return_value = responses['role']['all']
        roles = self.redmine.role.all()
        self.assertEqual(roles[0].id, 1)
        self.assertEqual(roles[0].name, 'Foo')
        self.assertEqual(roles[1].id, 2)
        self.assertEqual(roles[1].name, 'Bar')

    def test_news_version(self):
        self.assertEqual(self.redmine.news.resource_class.redmine_version, '1.1')

    def test_news_all(self):
        self.response.json.return_value = responses['news']['all']
        news = self.redmine.news.all()
        self.assertEqual(news[0].id, 1)
        self.assertEqual(news[0].title, 'Foo')
        self.assertEqual(news[1].id, 2)
        self.assertEqual(news[1].title, 'Bar')

    def test_news_filter(self):
        self.response.json.return_value = responses['news']['filter']
        news = self.redmine.news.filter(project_id=1)
        self.assertEqual(news[0].id, 1)
        self.assertEqual(news[0].title, 'Foo')
        self.assertEqual(news[1].id, 2)
        self.assertEqual(news[1].title, 'Bar')

    def test_issue_status_version(self):
        self.assertEqual(self.redmine.issue_status.resource_class.redmine_version, '1.3')

    def test_issue_status_all(self):
        self.response.json.return_value = responses['issue_status']['all']
        statuses = self.redmine.issue_status.all()
        self.assertEqual(statuses[0].id, 1)
        self.assertEqual(statuses[0].name, 'Foo')
        self.assertEqual(statuses[1].id, 2)
        self.assertEqual(statuses[1].name, 'Bar')

    def test_tracker_version(self):
        self.assertEqual(self.redmine.tracker.resource_class.redmine_version, '1.3')

    def test_tracker_all(self):
        self.response.json.return_value = responses['tracker']['all']
        trackers = self.redmine.tracker.all()
        self.assertEqual(trackers[0].id, 1)
        self.assertEqual(trackers[0].name, 'Foo')
        self.assertEqual(trackers[1].id, 2)
        self.assertEqual(trackers[1].name, 'Bar')

    def test_query_version(self):
        self.assertEqual(self.redmine.query.resource_class.redmine_version, '1.3')

    def test_query_all(self):
        self.response.json.return_value = responses['query']['all']
        queries = self.redmine.query.all()
        self.assertEqual(queries[0].id, 1)
        self.assertEqual(queries[0].name, 'Foo')
        self.assertEqual(queries[1].id, 2)
        self.assertEqual(queries[1].name, 'Bar')

    def test_custom_field_version(self):
        self.assertEqual(self.redmine.custom_field.resource_class.redmine_version, '2.4')

    def test_custom_field_all(self):
        self.response.json.return_value = responses['custom_field']['all']
        fields = self.redmine.custom_field.all()
        self.assertEqual(fields[0].id, 1)
        self.assertEqual(fields[0].name, 'Foo')
        self.assertEqual(fields[1].id, 2)
        self.assertEqual(fields[1].name, 'Bar')

    def test_custom_field_return_value_even_if_there_is_none(self):
        self.response.json.return_value = responses['custom_field']['all']
        fields = self.redmine.custom_field.all()
        self.assertEqual(fields[0].id, 1)
        self.assertEqual(fields[0].name, 'Foo')
        self.assertEqual(fields[0].value, 0)
