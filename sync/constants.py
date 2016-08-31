ATTRIBUTEMASK_TAG = '{http://schemas.microsoft.com/ado/2007/08/dataservices}AttributeMask'
CONTENT_TAG = '{http://www.w3.org/2005/Atom}content'
ENTRY_TAG = '{http://www.w3.org/2005/Atom}entry'
ID_TAG = '{http://schemas.microsoft.com/ado/2007/08/dataservices}Id'
LINK_TAG = '{http://www.w3.org/2005/Atom}link'
MESSAGE_TAG = '{http://schemas.microsoft.com/ado/2007/08/dataservices/metadata}message'

TYPE_KEY = '{http://schemas.microsoft.com/ado/2007/08/dataservices/metadata}type'


FORBIDDEN_ENTITIES = (
    'Competitor',
    'ConstraintBasedGroup',
    'Contract',
    'ContractDetail',
    'ContractTemplate',
    'CustomerOpportunityRole',
    'CustomerRelationship',
    'Discount',
    'DiscountType',
    'Invoice',
    'InvoiceDetail',
    'Lead',
    'LookUpMapping',
    'Opportunity',
    'OpportunityProduct',
    'OrganizationUI',
    'Post',
    'PostComment',
    'PostFollow',
    'PostLike',
    'PriceLevel',
    'Product',
    'ProductPriceLevel',
    'Quote',
    'QuoteDetail',
    'RelationshipRole',
    'RelationshipRoleMap',
    'Resource',
    'ResourceGroup',
    'ResourceSpec',
    'SalesLiterature',
    'SalesLiteratureItem',
    'SalesOrder',
    'SalesOrderDetail',
    'Service',
    'Territory',
    'UoM',
    'UoMSchedule',
    'detica_optionsetfield',
    'detica_portalpage',
    'mtc_licensing',
    'optevia_omisorder',
    'optevia_uktiorder',
)

ALL_ENTITY_NAMES = (
    'Account',
    'AccountLeads',
    'ActivityMimeAttachment',
    'ActivityParty',
    'ActivityPointer',
    'Annotation',
    'AnnualFiscalCalendar',
    'Appointment',
    'AsyncOperation',
    'AttributeMap',
    'Audit',
    'BulkDeleteFailure',
    'BulkDeleteOperation',
    'BulkOperation',
    'BulkOperationLog',
    'BusinessUnit',
    'BusinessUnitNewsArticle',
    'Calendar',
    'Campaign',
    'CampaignActivity',
    'CampaignActivityItem',
    'CampaignItem',
    'CampaignResponse',
    'ColumnMapping',
    'Competitor',
    'CompetitorProduct',
    'CompetitorSalesLiterature',
    'Connection',
    'ConnectionRole',
    'ConnectionRoleAssociation',
    'ConnectionRoleObjectTypeCode',
    'ConstraintBasedGroup',
    'Contact',
    'ContactInvoices',
    'ContactLeads',
    'ContactOrders',
    'ContactQuotes',
    'Contract',
    'ContractDetail',
    'ContractTemplate',
    'CustomerAddress',
    'CustomerOpportunityRole',
    'CustomerRelationship',
    'Dependency',
    'Discount',
    'DiscountType',
    'DisplayString',
    'DuplicateRecord',
    'DuplicateRule',
    'DuplicateRuleCondition',
    'Email',
    'EntityMap',
    'Equipment',
    'Fax',
    'FieldPermission',
    'FieldSecurityProfile',
    'FixedMonthlyFiscalCalendar',
    'Goal',
    'GoalRollupQuery',
    'Import',
    'ImportEntityMapping',
    'ImportFile',
    'ImportJob',
    'ImportLog',
    'ImportMap',
    'Incident',
    'IncidentResolution',
    'InvalidDependency',
    'Invoice',
    'InvoiceDetail',
    'IsvConfig',
    'KbArticle',
    'KbArticleComment',
    'KbArticleTemplate',
    'Lead',
    'LeadAddress',
    'LeadCompetitors',
    'LeadProduct',
    'Letter',
    'License',
    'List',
    'ListMember',
    'LookUpMapping',
    'MailMergeTemplate',
    'Metric',
    'MonthlyFiscalCalendar',
    'Opportunity',
    'OpportunityClose',
    'OpportunityCompetitors',
    'OpportunityProduct',
    'OrderClose',
    'Organization',
    'OrganizationUI',
    'OwnerMapping',
    'PhoneCall',
    'PickListMapping',
    'PluginAssembly',
    'PluginType',
    'PluginTypeStatistic',
    'Post',
    'PostComment',
    'PostFollow',
    'PostLike',
    'PriceLevel',
    'PrincipalObjectAttributeAccess',
    'Privilege',
    'ProcessSession',
    'Product',
    'ProductAssociation',
    'ProductPriceLevel',
    'ProductSalesLiterature',
    'ProductSubstitute',
    'Publisher',
    'PublisherAddress',
    'QuarterlyFiscalCalendar',
    'Queue',
    'QueueItem',
    'Quote',
    'QuoteClose',
    'QuoteDetail',
    'RecurrenceRule',
    'RecurringAppointmentMaster',
    'RelationshipRole',
    'RelationshipRoleMap',
    'Report',
    'ReportCategory',
    'ReportEntity',
    'ReportLink',
    'ReportVisibility',
    'Resource',
    'ResourceGroup',
    'ResourceSpec',
    'Role',
    'RolePrivileges',
    'RollupField',
    'SalesLiterature',
    'SalesLiteratureItem',
    'SalesOrder',
    'SalesOrderDetail',
    'SavedQuery',
    'SavedQueryVisualization',
    'SdkMessage',
    'SdkMessageFilter',
    'SdkMessagePair',
    'SdkMessageProcessingStep',
    'SdkMessageProcessingStepImage',
    'SdkMessageProcessingStepSecureConfig',
    'SdkMessageRequest',
    'SdkMessageRequestField',
    'SdkMessageResponse',
    'SdkMessageResponseField',
    'SemiAnnualFiscalCalendar',
    'Service',
    'ServiceAppointment',
    'ServiceContractContacts',
    'ServiceEndpoint',
    'SharePointDocumentLocation',
    'SharePointSite',
    'Site',
    'SiteMap',
    'Solution',
    'SolutionComponent',
    'Subject',
    'SystemForm',
    'SystemUser',
    'SystemUserLicenses',
    'SystemUserProfiles',
    'SystemUserRoles',
    'Task',
    'Team',
    'TeamMembership',
    'TeamProfiles',
    'TeamRoles',
    'Template',
    'Territory',
    'TimeZoneDefinition',
    'TimeZoneLocalizedName',
    'TimeZoneRule',
    'TransactionCurrency',
    'TransformationMapping',
    'TransformationParameterMapping',
    'UoM',
    'UoMSchedule',
    'UserEntityInstanceData',
    'UserEntityUISettings',
    'UserForm',
    'UserQuery',
    'UserQueryVisualization',
    'UserSettings',
    'WebResource',
    'Workflow',
    'WorkflowDependency',
    'WorkflowLog',
    'detica_aboutsupportprovided',
    'detica_accesstoclients',
    'detica_accesstomarket',
    'detica_accesstoresources',
    'detica_accountclassification',
    'detica_cancellationreason',
    'detica_citydeal',
    'detica_citydealrole',
    'detica_claimsprovider',
    'detica_clientrequirementcomplexity',
    'detica_comment',
    'detica_companynameshared',
    'detica_costreduction',
    'detica_decisionmakerknown',
    'detica_detica_omisorder_contact',
    'detica_discountrate',
    'detica_duplicateintersection',
    'detica_duplicaterecordpointer',
    'detica_enterprisezone',
    'detica_enterprisezonerole',
    'detica_growthpotential',
    'detica_hourlyrate',
    'detica_incentivedriven',
    'detica_interaction',
    'detica_investmentabovethreshold',
    'detica_investmentdeliverypartner',
    'detica_investmentdeliverypartnerrole',
    'detica_investmentdriver',
    'detica_investmentrdelement',
    'detica_investmentsreputationenhancement',
    'detica_investmentstrategicpoliticalimportance',
    'detica_investorcredibility',
    'detica_investorquality',
    'detica_investortrackrecord',
    'detica_investorukpreference',
    'detica_issueimpact',
    'detica_issueragstatus',
    'detica_issueresolvedok',
    'detica_issueurgency',
    'detica_legacyportaluser',
    'detica_localauthority',
    'detica_localauthorityrole',
    'detica_newexistinginvestor',
    'detica_newjobscreated',
    'detica_omisorder',
    'detica_optevia_servicedelivery_detica_typeofsu',
    'detica_optionsetfield',
    'detica_orderactivity',
    'detica_orderadvisorresource',
    'detica_ordermarketresource',
    'detica_orderparty',
    'detica_orderresource',
    'detica_orderstatushistory',
    'detica_orgspecificissue',
    'detica_parentcompanyturnover',
    'detica_payment',
    'detica_portalpage',
    'detica_portalprompt',
    'detica_projectadvisorrole',
    'detica_projectbringsnewworld',
    'detica_projectcitydeal',
    'detica_projectcompetitorlocation',
    'detica_projectenterprisezone',
    'detica_projectfunding',
    'detica_projecthasrdcomponent',
    'detica_projectinvestmentdeliverypartner',
    'detica_projectlinked',
    'detica_projectlocalauthority',
    'detica_projectstage',
    'detica_projecttransferred',
    'detica_projectvalue',
    'detica_projectwillland',
    'detica_proximitytosupplier',
    'detica_refund',
    'detica_regulatorydriven',
    'detica_salaryabovethreshold',
    'detica_servicedeliveryadvisor',
    'detica_settings',
    'detica_skilledresourcelevel',
    'detica_skillsseeking',
    'detica_specialistdeliveryprovider',
    'detica_specificinvestmentprogramme',
    'detica_surveyresult',
    'detica_technologyseeking',
    'detica_typeofsupportprovided',
    'detica_userprincipalname',
    'detica_worldpayconfig',
    'mtc_licensing',
    'mtcsp_spellcheckersetting',
    'optevia_activitylink',
    'optevia_address',
    'optevia_addresstype',
    'optevia_advisorrole',
    'optevia_balancesheetrange',
    'optevia_businessstream',
    'optevia_businesstype',
    'optevia_communicationchannel',
    'optevia_communicationpreference',
    'optevia_companieshousestatus',
    'optevia_contactaffiliation',
    'optevia_contactrole',
    'optevia_country',
    'optevia_customactivitylog',
    'optevia_databasesource',
    'optevia_emailaddress',
    'optevia_emailaddresstype',
    'optevia_employeerange',
    'optevia_event',
    'optevia_eventserviceprovider',
    'optevia_eventserviceproviderrole',
    'optevia_eventtype',
    'optevia_exportexperience',
    'optevia_exportlog',
    'optevia_fdiaftercarevisit',
    'optevia_fdiaftercarevisitpriority',
    'optevia_fdiaftercarevisitserviceprovider',
    'optevia_fdiaftercarevisittask',
    'optevia_fdiaftercarevisittaskeventscore',
    'optevia_fdiaftercarevisittaskpriority',
    'optevia_fdiaftercarevisittasktype',
    'optevia_gender',
    'optevia_governmentfinancialassistance',
    'optevia_interaction',
    'optevia_interactioncommunicationchannel',
    'optevia_interactionissue',
    'optevia_interactionissuetype',
    'optevia_interactionuse',
    'optevia_internalproject',
    'optevia_internationallymobile',
    'optevia_investmentexperience',
    'optevia_investmenttype',
    'optevia_issue',
    'optevia_issuetype',
    'optevia_jobnoaverage',
    'optevia_knowledgedriven',
    'optevia_language',
    'optevia_levelofinvolvement',
    'optevia_locationtype',
    'optevia_nationality',
    'optevia_omisorder',
    'optevia_organisationcountry',
    'optevia_organisationcountrylevelofinterest',
    'optevia_organisationorganisationtype',
    'optevia_organisationsector',
    'optevia_organisationsize',
    'optevia_organisationtype',
    'optevia_probabilityofsuccess',
    'optevia_programme',
    'optevia_programmeinternalproject',
    'optevia_project',
    'optevia_projectcountry',
    'optevia_projectnature',
    'optevia_projectorganisation',
    'optevia_projectorganisationrole',
    'optevia_projectsector',
    'optevia_projectserviceprovider',
    'optevia_projectserviceproviderrole',
    'optevia_projectstatus',
    'optevia_projecttype',
    'optevia_projectukregion',
    'optevia_projectukregionrole',
    'optevia_quotable',
    'optevia_referralsource',
    'optevia_sector',
    'optevia_sectorhierarchylevel',
    'optevia_sectornatureofinterest',
    'optevia_service',
    'optevia_servicedelivery',
    'optevia_servicedeliverystatus',
    'optevia_serviceoffer',
    'optevia_serviceoffercountry',
    'optevia_serviceproviderrole',
    'optevia_serviceprovidertype',
    'optevia_servicetype',
    'optevia_telephone',
    'optevia_telephonetype',
    'optevia_title',
    'optevia_tooltip',
    'optevia_turnoverrange',
    'optevia_ukregion',
    'optevia_uktiorder',
)

ENTITY_NAMES = [
    name for name in ALL_ENTITY_NAMES if name not in FORBIDDEN_ENTITIES
]

ENTITY_INT_MAP = {
    name: index for index, name in enumerate(ENTITY_NAMES)
}
