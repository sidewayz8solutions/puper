const HomePage: React.FC = () => {
  return (
    <div className="flex h-full">
      {/* Search Panel */}
      <SearchPanel />

      {/* Map Area */}
      <div className="flex-1 relative">
        <MapComponent className="w-full h-full" />
      </div>
    </div>
  );
};

export default HomePage;
