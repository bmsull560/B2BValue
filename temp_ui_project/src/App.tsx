import React, { useState, useEffect } from 'react';

// Main App component for the B2BValue GTM Interface
const App = () => {
  // State to manage the active view/page
  const [activeView, setActiveView] = useState('dashboard');
  // State to hold any messages, e.g., for modal dialogs
  const [message, setMessage] = useState(null);

  /**
   * Displays a temporary message to the user, similar to an alert but within the UI.
   * @param {string} msg - The message to display.
   * @param {string} type - The type of message (e.g., 'success', 'error', 'info').
   */
  const showMessage = (msg, type = 'info') => {
    setMessage({ text: msg, type });
    // Automatically clear the message after 3 seconds
    setTimeout(() => {
      setMessage(null);
    }, 3000);
  };

  /**
   * Helper component for confidence indicators (circular display)
   * Emulates Shadcn's circular progress or badge style.
   * @param {object} props - Component properties
   * @param {number} props.percentage - The percentage value to display.
   * @param {string} props.label - Label for the indicator.
   * @param {string} props.colorClass - Tailwind CSS class for primary color (e.g., 'border-emerald-500').
   */
  const ConfidenceIndicator = ({ percentage, label, colorClass }) => (
    <div className="flex flex-col items-center justify-center p-3 bg-black rounded-lg shadow-sm border border-white">
      <div className={`relative w-20 h-20 rounded-full border-2 ${colorClass} flex items-center justify-center`}>
        <span className={`text-xl font-bold ${colorClass.replace('border-', 'text-')}`}>{percentage}%</span>
      </div>
      <p className="mt-1 text-xs text-white">{label}</p>
    </div>
  );

  /**
   * Renders the main content based on the activeView state.
   * Each case represents a different section of the application.
   */
  const renderContent = () => {
    // Shared button styles for the neon green accent
    const neonGreenButtonClass = "inline-flex items-center justify-center whitespace-nowrap rounded-md text-sm font-medium transition-colors focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-emerald-500 disabled:pointer-events-none disabled:opacity-50 bg-emerald-500 text-gray-900 shadow-md hover:bg-emerald-400 h-8 px-3 py-1";
    const secondaryButtonClass = "inline-flex items-center justify-center whitespace-nowrap rounded-md text-sm font-medium transition-colors focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-emerald-500 disabled:pointer-events-none disabled:opacity-50 bg-white text-black shadow-sm hover:bg-gray-100 h-8 px-3 py-1";
    const ghostButtonClass = "inline-flex items-center justify-center whitespace-nowrap rounded-md text-sm font-medium transition-colors focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-emerald-500 disabled:pointer-events-none disabled:opacity-50 text-emerald-400 hover:text-emerald-300 h-8 px-3 py-1";
    const inputClass = "flex h-9 w-full rounded-md border border-white bg-black px-3 py-2 text-sm text-white ring-offset-background file:border-0 file:bg-transparent file:text-sm file:font-medium placeholder:text-gray-400 focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-emerald-500 disabled:cursor-not-allowed disabled:opacity-50";
    const textareaClass = "flex min-h-[60px] w-full rounded-md border border-white bg-black px-3 py-2 text-sm text-white ring-offset-background placeholder:text-gray-400 focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-emerald-500 disabled:cursor-not-allowed disabled:opacity-50";
    const selectClass = "flex h-9 w-full items-center justify-between rounded-md border border-white bg-black px-3 py-2 text-sm text-white ring-offset-background focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-emerald-500 disabled:cursor-not-allowed disabled:opacity-50 [&>span]:line-clamp-1";

    switch (activeView) {
      case 'dashboard':
        return (
          <div className="p-4">
            <h2 className="text-3xl font-bold text-white mb-6">Welcome back, John!</h2>

            {/* Action Cards */}
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-8">
              <div className="bg-black p-4 rounded-lg shadow-lg flex flex-col items-center justify-center text-center border border-white">
                <i className="fas fa-file-alt text-3xl text-emerald-400 mb-2"></i>
                <h3 className="text-base font-semibold text-white mb-1">Create Business Case</h3>
                <p className="text-gray-300 text-xs mb-3">Start a new value analysis.</p>
                <button
                  onClick={() => setActiveView('project-intake')}
                  className={neonGreenButtonClass}
                >
                  Create Case
                </button>
              </div>
              <div className="bg-black p-4 rounded-lg shadow-lg flex flex-col items-center justify-center text-center border border-white">
                <i className="fas fa-th-large text-3xl text-emerald-400 mb-2"></i>
                <h3 className="text-base font-semibold text-white mb-1">Use a Template</h3>
                <p className="text-gray-300 text-xs mb-3">Jumpstart analysis with templates.</p>
                <button
                  onClick={() => setActiveView('templates')}
                  className={neonGreenButtonClass}
                >
                  Use Template
                </button>
              </div>
              <div className="bg-black p-4 rounded-lg shadow-lg flex flex-col items-center justify-center text-center border border-white">
                <i className="fas fa-history text-3xl text-emerald-400 mb-2"></i>
                <h3 className="text-base font-semibold text-white mb-1">View Recent</h3>
                <p className="text-gray-300 text-xs mb-3">Access your recent analyses.</p>
                <button
                  onClick={() => setActiveView('reports')}
                  className={neonGreenButtonClass}
                >
                  View Recent
                </button>
              </div>
            </div>

            {/* Recent Activity & Performance Summary Section */}
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
              {/* Recent Activity Card */}
              <div className="bg-black p-4 rounded-lg shadow-lg border border-white">
                <h3 className="text-lg font-semibold text-white mb-4">Recent Activity</h3>
                <ul className="space-y-2 text-sm">
                  <li className="flex items-center text-white">
                    <i className="fas fa-inbox text-emerald-400 mr-3 text-base"></i>
                    <span>You were invited to collaborate on "<span className="text-emerald-300">Healthcare ROI Analysis</span>".</span>
                    <span className="ml-auto text-xs text-gray-400">2h ago</span>
                  </li>
                  <li className="flex items-center text-white">
                    <i className="fas fa-file-alt text-emerald-400 mr-3 text-base"></i>
                    <span>"<span className="text-emerald-300">Manufacturing Efficiency Business Case</span>" completed.</span>
                    <span className="ml-auto text-xs text-gray-400">Yesterday</span>
                  </li>
                  <li className="flex items-center text-white">
                    <i className="fas fa-chart-line text-emerald-400 mr-3 text-base"></i>
                    <span>"<span className="text-emerald-300">Q1 Performance Summary</span>" report generated.</span>
                    <span className="ml-auto text-xs text-gray-400">3d ago</span>
                  </li>
                </ul>
              </div>

              {/* Performance Summary Card */}
              <div className="bg-black p-4 rounded-lg shadow-lg border border-white">
                <h3 className="text-lg font-semibold text-white mb-4">Performance Summary</h3>
                <div className="flex items-center justify-around text-center mb-4">
                  <div>
                    <p className="text-2xl font-bold text-emerald-400">34</p>
                    <p className="text-white text-xs">Cases Created</p>
                  </div>
                  <div>
                    <p className="text-2xl font-bold text-emerald-400">84%</p>
                    <p className="text-white text-xs">Avg. ROI (Estimated)</p>
                  </div>
                </div>
                <div className="h-20 bg-white rounded-md flex items-center justify-center text-black text-xs border border-black">
                  <p>Small trend chart visualization here</p>
                </div>
              </div>
            </div>
          </div>
        );
      case 'project-intake':
        return (
            <div className="p-4">
                <h2 className="text-3xl font-bold text-white mb-6">New Project Intake</h2>
                <p className="text-white text-sm mb-4">
                    Provide initial details for your project to begin the AI-powered business value analysis.
                    This input will be processed by the <strong className="text-emerald-400">Intake Assistant Agent</strong>.
                </p>
                <div className="bg-black p-5 rounded-lg shadow-lg grid grid-cols-1 lg:grid-cols-2 gap-5 border border-white">
                    {/* Input Form Section */}
                    <div className="space-y-4">
                        <div>
                            <label htmlFor="companyName" className="block text-sm font-medium text-white mb-1">Company Name</label>
                            <input
                                type="text"
                                id="companyName"
                                className={inputClass}
                                placeholder="e.g., Acme Corp"
                            />
                        </div>
                        <div>
                            <label htmlFor="dealSize" className="block text-sm font-medium text-white mb-1">Deal Size ($)</label>
                            <input
                                type="number"
                                id="dealSize"
                                className={inputClass}
                                placeholder="e.g., 1,000,000"
                            />
                        </div>
                        <div>
                            <label htmlFor="timeline" className="block text-sm font-medium text-white mb-1">Timeline</label>
                            <select
                                id="timeline"
                                className={selectClass}
                            >
                                <option value="" className="text-gray-400 bg-black">Select...</option>
                                <option value="1-3-months" className="bg-black text-white">1-3 Months</option>
                                <option value="3-6-months" className="bg-black text-white">3-6 Months</option>
                                <option value="6-12-months" className="bg-black text-white">6-12 Months</option>
                                <option value="12-plus-months" className="bg-black text-white">12+ Months</option>
                            </select>
                        </div>
                        <div>
                            <label className="block text-sm font-medium text-white mb-2">Target Personas</label>
                            <div className="flex flex-wrap gap-3 text-sm">
                                <label className="inline-flex items-center cursor-pointer">
                                    <input type="checkbox" className="form-checkbox h-4 w-4 text-emerald-500 rounded border-white bg-black focus:ring-emerald-500" />
                                    <span className="ml-2 text-white">CRO</span>
                                </label>
                                <label className="inline-flex items-center cursor-pointer">
                                    <input type="checkbox" className="form-checkbox h-4 w-4 text-emerald-500 rounded border-white bg-black focus:ring-emerald-500" />
                                    <span className="ml-2 text-white">CFO</span>
                                </label>
                                <label className="inline-flex items-center cursor-pointer">
                                    <input type="checkbox" className="form-checkbox h-4 w-4 text-emerald-500 rounded border-white bg-black focus:ring-emerald-500" />
                                    <span className="ml-2 text-white">COO</span>
                                </label>
                                <label className="inline-flex items-center cursor-pointer">
                                    <input type="checkbox" className="form-checkbox h-4 w-4 text-emerald-500 rounded border-white bg-black focus:ring-emerald-500" />
                                    <span className="ml-2 text-white">Sales Leader</span>
                                </label>
                            </div>
                        </div>
                        <div>
                            <label htmlFor="documentUpload" className="block text-sm font-medium text-white mb-1">Document Upload</label>
                            <div className="flex justify-center items-center px-4 pt-3 pb-4 border-2 border-white border-dashed rounded-md cursor-pointer bg-black hover:bg-gray-900 transition-colors duration-200">
                                <div className="text-center">
                                    <svg className="mx-auto h-10 w-10 text-white" stroke="currentColor" fill="none" viewBox="0 0 48 48" aria-hidden="true">
                                        <path d="M28 8H12a2 2 0 00-2 2v20m32-12v8m0 0v8a2 2 0 01-2 2H12a2 2 0 01-2-2v-2m20-12V8a2 2 0 00-2-2h-8a2 2 0 00-2 2v12m9 2h3m-3 0a2 2 0 002 2H9a2 2 0 00-2 2v8a2 2 0 002 2h2m-2-8h8m-8 0a2 2 0 002 2h-2m2 0a2 2 0 002 2h-2" />
                                    </svg>
                                    <p className="mt-1 text-xs text-white">
                                        <label htmlFor="file-upload" className="relative cursor-pointer rounded-md font-medium text-emerald-400 hover:text-emerald-300 focus-within:outline-none focus-within:ring-2 focus-within:ring-offset-2 focus-within:ring-emerald-500">
                                            <span>Drag and drop or browse</span>
                                            <input id="file-upload" name="file-upload" type="file" className="sr-only" />
                                        </label>
                                    </p>
                                    <p className="text-xs text-gray-400">PDF, DOCX, XLSX, etc. up to 10MB</p>
                                </div>
                            </div>
                            <div className="mt-2 text-xs text-white">
                                <p className="flex items-center"><i className="fas fa-file-pdf mr-2 text-red-400"></i> requirements.pdf</p>
                            </div>
                        </div>
                        <button
                            type="button"
                            onClick={() => showMessage('Submitting project details to Intake Assistant...', 'info')}
                            className={neonGreenButtonClass + " w-full"}
                        >
                            Start Analysis
                        </button>
                    </div>
                    {/* Tips Section */}
                    <div className="bg-white p-4 rounded-lg border border-black h-full">
                        <h3 className="text-lg font-semibold text-black mb-3">Tips for Opportunity Details</h3>
                        <ul className="list-disc list-inside text-black space-y-2 text-sm">
                            <li>Provide clear, concise company details for accurate analysis.</li>
                            <li>Estimate Deal Size to help prioritize the business case.</li>
                            <li>Select a realistic Timeline for project completion.</li>
                            <li>Choose relevant Target Personas to tailor value propositions.</li>
                            <li>Upload relevant documents (e.g., requirements, existing reports) for richer context.</li>
                        </ul>
                    </div>
                </div>
            </div>
        );
      case 'ai-analysis':
        return (
          <div className="p-4">
            <h2 className="text-3xl font-bold text-white mb-6">AI Analysis Results</h2>
            <p className="text-white text-sm mb-5">
              Review the AI's assessment of your project, including confidence levels, value drivers, and recommendations.
              This is driven by various agents, including the <strong className="text-emerald-400">Confidence Scoring Agent</strong> and <strong className="text-emerald-400">Value Driver Agent</strong>.
            </p>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-8">
                <ConfidenceIndicator percentage={92} label="High Confidence" colorClass="border-emerald-500 text-emerald-500" />
                <ConfidenceIndicator percentage={78} label="Medium Confidence" colorClass="border-yellow-500 text-yellow-500" />
                <ConfidenceIndicator percentage={45} label="Low Confidence" colorClass="border-red-500 text-red-500" />
            </div>

            <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
                {/* Value Driver Breakdown */}
                <div className="bg-black p-5 rounded-lg shadow-lg border border-white">
                    <h3 className="text-xl font-semibold text-white mb-4">Value Driver Breakdown</h3>
                    <ul className="space-y-3 text-white text-base">
                        <li className="flex justify-between items-center pb-2 border-b border-white">
                            <span>Cost Savings</span>
                            <span className="font-bold text-emerald-400">38% Impact</span>
                        </li>
                        <li className="flex justify-between items-center py-2 border-b border-white">
                            <span>Productivity Gains</span>
                            <span className="font-bold text-emerald-400">70% Impact</span>
                        </li>
                        <li className="flex justify-between items-center py-2 border-b border-white">
                            <span>Risk Reduction</span>
                            <span className="font-bold text-emerald-400">85% Impact</span>
                        </li>
                        <li className="flex justify-between items-center pt-2">
                            <span>Revenue Growth</span>
                            <span className="font-bold text-emerald-400">40% Impact</span>
                        </li>
                    </ul>
                    <div className="mt-6 pt-4 border-t border-white flex justify-between items-center text-lg font-bold text-white">
                        <span>Total Estimated ROI</span>
                        <span className="text-emerald-400">189%</span>
                    </div>
                </div>

                {/* AI Explanation & Recommendations */}
                <div className="bg-black p-5 rounded-lg shadow-lg border border-white">
                    <h3 className="text-xl font-semibold text-white mb-4">AI Explanation & Key Insights</h3>
                    <div className="text-white text-sm space-y-3">
                        <p>
                            <strong className="text-emerald-400">AI Explanation:</strong> Our analysis indicates a medium confidence that the proposed solution
                            will lead to significant productivity improvements and moderate cost savings.
                        </p>
                        <p>
                            <strong className="text-emerald-400">Key Insight 1:</strong> Requires precise data integration to measure direct process improvements efficiently.
                        </p>
                        <p>
                            <strong className="text-emerald-400">Key Insight 2:</strong> Potential for revenue growth opportunities if lead conversion rates are improved post-implementation.
                        </p>
                    </div>
                    <h3 className="text-xl font-semibold text-white mt-6 mb-4">Recommendations</h3>
                    <ul className="space-y-3 text-white text-sm">
                        <li className="flex justify-between items-center pb-2 border-b border-white">
                            <span>Recommendation 1: Optimize data ingestion workflows.</span>
                            <button
                                onClick={() => showMessage('Reviewing Recommendation 1...', 'info')}
                                className={ghostButtonClass}
                            >
                                Review <i className="fas fa-arrow-right ml-1"></i>
                            </button>
                        </li>
                        <li className="flex justify-between items-center pt-2">
                            <span>Recommendation 2: Conduct a detailed lead conversion study.</span>
                            <button
                                onClick={() => showMessage('Sharing Recommendation 2...', 'info')}
                                className={ghostButtonClass}
                            >
                                Share <i className="fas fa-share-alt ml-1"></i>
                            </button>
                        </li>
                    </ul>
                    <div className="mt-6 pt-4 border-t border-white flex justify-end space-x-3">
                        <button
                            onClick={() => showMessage('Analysis accepted and saved.', 'success')}
                            className={neonGreenButtonClass}
                        >
                            Accept
                        </button>
                        <button
                            onClick={() => showMessage('Analysis rejected. Sending feedback to Critique Agent.', 'error')}
                            className="inline-flex items-center justify-center whitespace-nowrap rounded-md text-sm font-medium transition-colors focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-red-500 disabled:pointer-events-none disabled:opacity-50 bg-red-600 text-white shadow-sm hover:bg-red-500 h-8 px-3 py-1"
                        >
                            Reject
                        </button>
                    </div>
                </div>
            </div>
          </div>
        );
      case 'roi-calculator':
        return (
          <div className="p-4">
            <h2 className="text-3xl font-bold text-white mb-6">ROI Calculator</h2>
            <p className="text-white text-sm mb-5">
              Calculate the potential return on investment for your initiatives. This is powered by the <strong className="text-emerald-400">ROI Calculator Agent</strong>.
            </p>
            <div className="bg-black p-5 rounded-lg shadow-lg border border-white">
              <form className="space-y-4">
                <div>
                  <label htmlFor="initialInvestment" className="block text-sm font-medium text-white mb-1">Initial Investment ($)</label>
                  <input
                    type="number"
                    id="initialInvestment"
                    className={inputClass}
                    placeholder="e.g., 50000"
                  />
                </div>
                <div>
                  <label htmlFor="expectedRevenueGain" className="block text-sm font-medium text-white mb-1">Expected Annual Revenue Gain ($)</label>
                  <input
                    type="number"
                    id="expectedRevenueGain"
                    className={inputClass}
                    placeholder="e.g., 150000"
                  />
                </div>
                <div>
                  <label htmlFor="annualCostSavings" className="block text-sm font-medium text-white mb-1">Annual Cost Savings ($)</label>
                  <input
                    type="number"
                    id="annualCostSavings"
                    className={inputClass}
                    placeholder="e.g., 20000"
                  />
                </div>
                <div>
                  <label htmlFor="timeHorizon" className="block text-sm font-medium text-white mb-1">Time Horizon (Years)</label>
                  <input
                    type="number"
                    id="timeHorizon"
                    className={inputClass}
                    placeholder="e.g., 3"
                  />
                </div>
                <button
                  type="button"
                  onClick={() => showMessage('Calculating ROI...', 'info')}
                  className={neonGreenButtonClass + " w-full"}
                >
                  Calculate ROI
                </button>
              </form>
              <p className="mt-5 text-center text-xl font-bold text-white">
                  <span className="text-emerald-400">Calculated ROI:</span> <span className="text-emerald-500">N/A</span>
              </p>
              <div className="mt-5 h-32 bg-white rounded-md flex items-center justify-center text-black text-xs border border-black">
                <p>Detailed ROI breakdown/chart here</p>
              </div>
            </div>
          </div>
        );
      case 'business-case-builder':
        return (
          <div className="p-4">
            <h2 className="text-3xl font-bold text-white mb-6">AI-Powered Business Case Builder</h2>
            <p className="text-white text-sm mb-5">
              Generate comprehensive business cases with AI assistance. This leverages the <strong className="text-emerald-400">Business Case Composer Agent</strong>
              and <strong className="text-emerald-400">Narrative Generator Agent</strong>.
            </p>
            <div className="bg-black p-5 rounded-lg shadow-lg border border-white">
              <form className="space-y-4">
                <div>
                  <label htmlFor="projectTitleBC" className="block text-sm font-medium text-white mb-1">Project Title</label>
                  <input
                    type="text"
                    id="projectTitleBC"
                    className={inputClass}
                    placeholder="e.g., AI-driven Customer Support Optimization"
                  />
                </div>
                <div>
                  <label htmlFor="projectObjectives" className="block text-sm font-medium text-white mb-1">Project Objectives</label>
                  <textarea
                    id="projectObjectives"
                    rows="3"
                    className={textareaClass}
                    placeholder="Clearly state what the project aims to achieve (e.g., 'Reduce customer support costs by 20%', 'Improve customer satisfaction by 15%')."
                  ></textarea>
                </div>
                <div>
                  <label htmlFor="targetAudience" className="block text-sm font-medium text-white mb-1">Target Audience (for Business Case)</label>
                  <input
                    type="text"
                    id="targetAudience"
                    className={inputClass}
                    placeholder="e.g., Executive Leadership, Sales Teams, IT Department"
                  />
                </div>
                <button
                  type="button"
                  onClick={() => showMessage('Building business case...', 'info')}
                  className={neonGreenButtonClass + " w-full"}
                >
                  Build Business Case
                </button>
              </form>
              <div className="mt-6 bg-white p-4 rounded-md border border-black">
                  <h3 className="text-lg font-bold text-black mb-2">Generated Business Case Summary:</h3>
                  <p className="text-gray-600 italic text-sm">Awaiting AI generation based on your inputs...</p>
                  <p className="text-xs text-gray-500 mt-2">
                    Confidence Score: <span className="text-emerald-400">N/A</span> | Feedback: <span className="text-gray-400">N/A</span>
                  </p>
              </div>
              <div className="mt-5 text-center">
                  <button
                    onClick={() => showMessage('Sending to Human Review Agent...', 'info')}
                    className="inline-flex items-center justify-center whitespace-nowrap rounded-md text-sm font-medium transition-colors focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-yellow-500 disabled:pointer-events-none disabled:opacity-50 bg-yellow-600 text-white shadow-sm hover:bg-yellow-500 h-8 px-3 py-1"
                  >
                    Send for Human Review
                  </button>
              </div>
            </div>
          </div>
        );
      case 'templates':
        return (
          <div className="p-4">
            <h2 className="text-3xl font-bold text-white mb-6">Industry-Specific Templates</h2>
            <p className="text-white text-sm mb-5">
              Select from a variety of pre-built frameworks tailored for different industries.
              These templates guide the analysis for various agents (e.g., <strong className="text-emerald-400">Template Selector Agent</strong>).
            </p>
            <div className="mb-5">
                <input
                    type="text"
                    placeholder="Search templates..."
                    className={inputClass}
                />
            </div>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              {[
                { name: 'Healthcare Optimization', desc: 'Optimize patient care workflows and reduce operational costs.' },
                { name: 'Manufacturing Efficiency', desc: 'Streamline production processes and improve resource utilization.' },
                { name: 'Retail Personalization', desc: 'Enhance customer experience and drive sales growth through personalization.' },
                { name: 'Financial Risk Assessment', desc: 'Identify and mitigate financial risks across portfolios.' },
                { name: 'Supply Chain Optimization', desc: 'Improve logistics, reduce lead times, and enhance supply chain resilience.' },
                { name: 'Customer Churn Prediction', desc: 'Predict and prevent customer churn using historical data.' },
              ].map((template, index) => (
                <div key={index} className="bg-black p-4 rounded-lg shadow-lg hover:shadow-xl transition-shadow duration-300 cursor-pointer border border-white">
                  <h3 className="text-lg font-semibold text-white mb-2">{template.name}</h3>
                  <p className="text-gray-300 text-xs mb-4">{template.desc}</p>
                  <button
                    onClick={() => showMessage(`Loading "${template.name}" template...`, 'info')}
                    className={secondaryButtonClass}
                  >
                    Select Template
                  </button>
                </div>
              ))}
            </div>
          </div>
        );
      case 'reports':
        return (
          <div className="p-4">
            <h2 className="text-3xl font-bold text-white mb-6">Comprehensive Reporting Capabilities</h2>
            <p className="text-white text-sm mb-5">
              Generate, view, and export detailed reports on your business value analyses. This integrates insights from the <strong className="text-emerald-400">Analytics Aggregator Agent</strong>.
            </p>
            <div className="bg-black p-5 rounded-lg shadow-lg border border-white">
              <h3 className="text-xl font-semibold text-white mb-4">Generated Reports</h3>
              <ul className="divide-y divide-white">
                {[
                  { name: 'Q1 2024 ROI Analysis', status: 'Completed', date: '2024-03-31' },
                  { name: 'Healthcare Pilot Business Case', status: 'Approved', date: '2024-04-15' },
                  { name: 'Manufacturing Cost Reduction Report', status: 'Completed', date: '2024-05-20' },
                  { name: 'AI-driven Customer Support Optimization - Narrative', status: 'Pending Review', date: '2024-06-12' },
                ].map((report, index) => (
                  <li key={index} className="py-3 flex flex-col sm:flex-row items-start sm:items-center justify-between">
                    <div className="mb-2 sm:mb-0">
                      <span className="text-base font-medium text-white block sm:inline">{report.name}</span>
                      <span className={`ml-0 sm:ml-2 text-xs px-2 py-0.5 rounded-full font-semibold ${
                        report.status === 'Completed' ? 'bg-emerald-700 text-emerald-100' :
                        report.status === 'Approved' ? 'bg-blue-700 text-blue-100' :
                        'bg-yellow-700 text-yellow-100'
                      }`}>
                        {report.status}
                      </span>
                      <p className="text-xs text-gray-400 mt-1 sm:mt-0">Generated: {report.date}</p>
                    </div>
                    <div className="flex flex-wrap gap-2">
                      <button
                        onClick={() => showMessage(`Viewing "${report.name}"...`, 'info')}
                        className={secondaryButtonClass}
                      >
                        View
                      </button>
                      <button
                        onClick={() => showMessage(`Exporting "${report.name}" to PDF...`, 'success')}
                        className="inline-flex items-center justify-center whitespace-nowrap rounded-md text-sm font-medium transition-colors focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-red-500 disabled:pointer-events-none disabled:opacity-50 bg-red-600 text-white shadow-sm hover:bg-red-500 h-8 px-3 py-1"
                      >
                        PDF
                      </button>
                      <button
                        onClick={() => showMessage(`Exporting "${report.name}" to Excel...`, 'success')}
                        className="inline-flex items-center justify-center whitespace-nowrap rounded-md text-sm font-medium transition-colors focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-green-500 disabled:pointer-events-none disabled:opacity-50 bg-green-600 text-white shadow-sm hover:bg-green-500 h-8 px-3 py-1"
                      >
                        Excel
                      </button>
                      {report.status === 'Pending Review' && (
                          <button
                            onClick={() => showMessage(`Navigating to review for "${report.name}"...`, 'info')}
                            className="inline-flex items-center justify-center whitespace-nowrap rounded-md text-sm font-medium transition-colors focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-yellow-500 disabled:pointer-events-none disabled:opacity-50 bg-yellow-600 text-white shadow-sm hover:bg-yellow-500 h-8 px-3 py-1"
                          >
                            Review
                          </button>
                      )}
                    </div>
                  </li>
                ))}
              </ul>
            </div>
          </div>
        );
      default:
        return <div className="p-4 text-white">Content not found.</div>;
    }
  };

  return (
    <div className="min-h-screen bg-black font-sans text-white antialiased">
      <style>
        {`
          @import url('https://api.fontshare.com/v2/css?f[]=satoshi@1,900,700,500,300,400&display=swap');
          .font-sans {
            font-family: 'Satoshi', sans-serif;
          }
        `}
      </style>
      <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/5.15.3/css/all.min.css"></link>

      {/* Global Message Display */}
      {message && (
        <div className={`fixed top-3 right-3 p-3 rounded-md shadow-lg z-50 text-sm transition-opacity duration-300 ${message.type === 'success' ? 'bg-emerald-500 text-black' : message.type === 'error' ? 'bg-red-500 text-white' : 'bg-blue-500 text-white'}`}>
          {message.text}
        </div>
      )}

      {/* Header */}
      <header className="bg-black shadow-lg py-3 px-5 flex items-center justify-between border-b border-white">
        <h1 className="text-2xl font-extrabold text-white">B2BValue GTM Interface</h1>
        <div className="flex items-center space-x-3">
          <span className="text-white text-base">Welcome, GTM Team!</span>
          <span className="text-xs text-gray-400">User ID: default-app-id</span>
          <button className="text-white hover:text-emerald-400 transition-colors duration-200">
            <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className="lucide lucide-settings"><path d="M12.22 2h-.44a2 2 0 0 0-2 2v.18a2 2 0 0 1-1 1.73l-.43.25a2 2 0 0 1-2 0l-.15-.08a2 2 0 0 0-2.73.73l-.22.39a2 2 0 0 0 .73 2.73l.09.15a2 2 0 0 1 0 2.73l-.09.15a2 2 0 0 0-.73 2.73l.22.39a2 2 0 0 0 2.73.73l.15-.08a2 2 0 0 1 2 0l.43.25a2 2 0 0 1 1 1.73V20a2 2 0 0 0 2 2h.44a2 2 0 0 0 2-2v-.18a2 2 0 0 1 1-1.73l.43-.25a2 2 0 0 1 2 0l.15.08a2 2 0 0 0 2.73-.73l.22-.39a2 2 0 0 0-.73-2.73l-.09-.15a2 2 0 0 1 0 2.73l.09-.15a2 2 0 0 0 .73-2.73l-.22-.39a2 2 0 0 0-2.73-.73l-.15.08a2 2 0 0 1-2 0l-.43-.25a2 2 0 0 1-1-1.73V4a2 2 0 0 0-2-2z"/><circle cx="12" cy="12" r="3"/></svg>
          </button>
        </div>
      </header>

      {/* Main Content Area */}
      <div className="flex flex-col md:flex-row min-h-[calc(100vh-64px)]">
        {/* Sidebar Navigation */}
        <nav className="bg-black text-white w-full md:w-60 p-4 space-y-2 flex-shrink-0 border-r border-white">
          <ul className="flex flex-col md:block">
            <li className="mb-1">
              <button
                onClick={() => setActiveView('dashboard')}
                className={`w-full flex items-center py-2 px-3 rounded-md transition-colors duration-200 text-base font-medium ${activeView === 'dashboard' ? 'bg-white text-emerald-400' : 'hover:bg-gray-900 hover:text-white'}`}
              >
                <i className="fas fa-tachometer-alt mr-2 text-lg"></i> Dashboard
              </button>
            </li>
            <li className="mb-1">
              <button
                onClick={() => setActiveView('project-intake')}
                className={`w-full flex items-center py-2 px-3 rounded-md transition-colors duration-200 text-base font-medium ${activeView === 'project-intake' ? 'bg-white text-emerald-400' : 'hover:bg-gray-900 hover:text-white'}`}
              >
                <i className="fas fa-plus-circle mr-2 text-lg"></i> Project Intake
              </button>
            </li>
            <li className="mb-1">
              <button
                onClick={() => setActiveView('ai-analysis')}
                className={`w-full flex items-center py-2 px-3 rounded-md transition-colors duration-200 text-base font-medium ${activeView === 'ai-analysis' ? 'bg-white text-emerald-400' : 'hover:bg-gray-900 hover:text-white'}`}
              >
                <i className="fas fa-brain mr-2 text-lg"></i> AI Analysis Results
              </button>
            </li>
            <li className="mb-1">
              <button
                onClick={() => setActiveView('roi-calculator')}
                className={`w-full flex items-center py-2 px-3 rounded-md transition-colors duration-200 text-base font-medium ${activeView === 'roi-calculator' ? 'bg-white text-emerald-400' : 'hover:bg-gray-900 hover:text-white'}`}
              >
                <i className="fas fa-calculator mr-2 text-lg"></i> ROI Calculator
              </button>
            </li>
            <li className="mb-1">
              <button
                onClick={() => setActiveView('business-case-builder')}
                className={`w-full flex items-center py-2 px-3 rounded-md transition-colors duration-200 text-base font-medium ${activeView === 'business-case-builder' ? 'bg-white text-emerald-400' : 'hover:bg-gray-900 hover:text-white'}`}
              >
                <i className="fas fa-briefcase mr-2 text-lg"></i> Business Case Builder
              </button>
            </li>
            <li className="mb-1">
              <button
                onClick={() => setActiveView('templates')}
                className={`w-full flex items-center py-2 px-3 rounded-md transition-colors duration-200 text-base font-medium ${activeView === 'templates' ? 'bg-white text-emerald-400' : 'hover:bg-gray-900 hover:text-white'}`}
              >
                <i className="fas fa-file-invoice mr-2 text-lg"></i> Templates
              </button>
            </li>
            <li className="mb-1">
              <button
                onClick={() => setActiveView('reports')}
                className={`w-full flex items-center py-2 px-3 rounded-md transition-colors duration-200 text-base font-medium ${activeView === 'reports' ? 'bg-white text-emerald-400' : 'hover:bg-gray-900 hover:text-white'}`}
              >
                <i className="fas fa-chart-pie mr-2 text-lg"></i> Reports
              </button>
            </li>
            <li className="mb-1">
                <button
                    onClick={() => showMessage('Settings page coming soon!', 'info')}
                    className="w-full flex items-center py-2 px-3 rounded-md transition-colors duration-200 text-base font-medium hover:bg-gray-900 hover:text-white"
                >
                    <i className="fas fa-cog mr-2 text-lg"></i> Settings
                </button>
            </li>
          </ul>
        </nav>

        {/* Dynamic Content Area */}
        <main className="flex-1 p-4 overflow-auto">
          {renderContent()}
        </main>
      </div>
    </div>
  );
};

export default App;